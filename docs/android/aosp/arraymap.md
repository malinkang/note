
## 构造函数

`ArrayMap`继承自`SimpleArrayMap`，`SimpleArrayMap`提供了3个构造函数


### 无参构造函数

无参构造函数，为`mHashes`和`mArray` 赋值。`mHashes`用来保存`Hash`值，`mHashes`数组是有序的，可以通过二分查找来获取索引。`mArray`用来保存`Key`和`Value`。

```java
//ContainerHelpers
static final int[] EMPTY_INTS = new int[0];
static final long[] EMPTY_LONGS = new long[0];
```

```java
public SimpleArrayMap() {
    mHashes = ContainerHelpers.EMPTY_INTS;
    mArray = ContainerHelpers.EMPTY_OBJECTS;
    mSize = 0;
}
```


### 指定容量

在创建ArrayMap时，可以指定容量。如果容量大于0，调用allocArrays来创建数组。

```java
public SimpleArrayMap(int capacity) {
    if (capacity == 0) {
        mHashes = ContainerHelpers.EMPTY_INTS;
        mArray = ContainerHelpers.EMPTY_OBJECTS;
    } else {
        allocArrays(capacity);
    }
    mSize = 0;
}
```


### 接收ArrayMap

还提供一个构造函数，可以传入一个`ArrayMap`。

```java
public SimpleArrayMap(SimpleArrayMap<K, V> map) {
    this();
    if (map != null) {
        putAll(map);
    }
}
```



## allocArrays()

allocArrays()负责创建mHashes和mArray。

ArrayMap中提供了两个静态数组mBaseCache和mTwiceBaseCache来缓存mHashes和mArray，因为这两个数组是静态的，所以所有的ArrayMap共享缓存。我们可以通过freeArrays来看ArrayMap是如何缓存的。

```java
private void allocArrays(final int size) {
    if (size == (BASE_SIZE*2)) {
        synchronized (SimpleArrayMap.class) {
            if (mTwiceBaseCache != null) {
                final Object[] array = mTwiceBaseCache;
                mArray = array;
                mTwiceBaseCache = (Object[])array[0];
                mHashes = (int[])array[1];
                array[0] = array[1] = null;
                mTwiceBaseCacheSize--;
                if (DEBUG) System.out.println(TAG + " Retrieving 2x cache " + mHashes
                        + " now have " + mTwiceBaseCacheSize + " entries");
                return;
            }
        }
    } else if (size == BASE_SIZE) {
        synchronized (SimpleArrayMap.class) {
            if (mBaseCache != null) {
                final Object[] array = mBaseCache;
                mArray = array;
                //取出上一个缓存并赋值给mBaseCache
                mBaseCache = (Object[])array[0];
               //取出mHashes
                mHashes = (int[])array[1];
                array[0] = array[1] = null;
                mBaseCacheSize--;
                if (DEBUG) System.out.println(TAG + " Retrieving 1x cache " + mHashes
                        + " now have " + mBaseCacheSize + " entries");
                return;
            }
        }
    }
    mHashes = new int[size];
    mArray = new Object[size<<1];
}
```



## freeArrays()

`freeArrays()`会被`clear()`调用。

`freeArrays`会用`mArray`的第一个元素来缓存当前缓存即`mBaseCache`，用第二个元素来缓存`mHashes`，其他元素设置为`null`，然后再将`mArray`赋值给`mBaseCache`。

```java
private static void freeArrays(final int[] hashes, final Object[] array, final int size) {
    if (hashes.length == (BASE_SIZE*2)) {
        synchronized (SimpleArrayMap.class) {
            if (mTwiceBaseCacheSize<CACHE_SIZE) {
                array[0] =mTwiceBaseCache;
                array[1] = hashes;
                for (int i=(size<<1)-1; i>=2; i--) {
                    array[i] = null;
                }
								mTwiceBaseCache= array;
							  mTwiceBaseCacheSize++;
                if (DEBUG) System.out.println(TAG+ " Storing 2x cache " + array
                        + " now have " +mTwiceBaseCacheSize+ " entries");
            }
        }
    } else if (hashes.length ==BASE_SIZE) {
        synchronized (SimpleArrayMap.class) {
            //如果缓存大小小于10
            if (mBaseCacheSize<CACHE_SIZE) {
                array[0] =mBaseCache
                array[1] = hashes;
                for (int i=(size<<1)-1; i>=2; i--) {
                    array[i] = null;
                }
								mBaseCache= array;
								mBaseCacheSize++;
                if (DEBUG) System.out.println(TAG+ " Storing 1x cache " + array
                        + " now have " +mBaseCacheSize+ " entries");
            }
        }
    }
}
```


## put()

```java
public V put(K key, V value) {
    final int osize = mSize;
    final int hash;
    int index;
    if (key == null) {
        hash = 0;
        index = indexOfNull();
    } else {
        //获取hash值
        hash = key.hashCode();
        index = indexOf(key, hash);
    }
    if (index >= 0) {
        index = (index<<1) + 1;
        final V old = (V)mArray[index];
        mArray[index] = value;
        return old;
    }

    index = ~index;
    if (osize >= mHashes.length) {
        // 第一次是4 第二次是8 第三次之后每次是原来的1.5倍
        final int n = osize >= (BASE_SIZE*2) ? (osize+(osize>>1))
                : (osize >= BASE_SIZE ? (BASE_SIZE*2) : BASE_SIZE);

        if (DEBUG) System.out.println(TAG + " put: grow from " + mHashes.length + " to " + n);

        final int[] ohashes = mHashes;
        final Object[] oarray = mArray;
        allocArrays(n);

        if (CONCURRENT_MODIFICATION_EXCEPTIONS && osize != mSize) {
            throw new ConcurrentModificationException();
        }

        if (mHashes.length > 0) {
            if (DEBUG) System.out.println(TAG + " put: copy 0-" + osize + " to 0");
            System.arraycopy(ohashes, 0, mHashes, 0, ohashes.length);
            System.arraycopy(oarray, 0, mArray, 0, oarray.length);
        }

        freeArrays(ohashes, oarray, osize);
    }

    if (index < osize) {
        if (DEBUG) System.out.println(TAG + " put: move " + index + "-" + (osize-index)
                + " to " + (index+1));
        System.arraycopy(mHashes, index, mHashes, index + 1, osize - index);
        System.arraycopy(mArray, index << 1, mArray, (index + 1) << 1, (mSize - index) << 1);
    }

    if (CONCURRENT_MODIFICATION_EXCEPTIONS) {
        if (osize != mSize || index >= mHashes.length) {
            throw new ConcurrentModificationException();
        }
    }

    mHashes[index] = hash;
    mArray[index<<1] = key;
    mArray[(index<<1)+1] = value;
    mSize++;
    return null;
}
```


## indexOf()


```java
int indexOf(Object key, int hash) {
    final int N = mSize;

    // Important fast case: if nothing is in here, nothing to look for.
    if (N == 0) {
        return ~0;
    }
  //通过二分查找找到合适的位置
  int index = binarySearchHashes(mHashes, N, hash);

    // If the hash code wasn't found, then we have no entry for this key.
    //如果小于0说明不存在
    if (index < 0) {
        return index;
    }

    // If the key at the returned index matches, that's what we want.
    //如果要存的key与对应位置的key相同 直接返回索引
    if (key.equals(mArray[index<<1])) {
        return index;
    }

    // Search for a matching key after the index.
    //hash值相同，key不相同 就遍历寻找key相同的，如果找不到key相同的就插入到end位置
    int end;
    for (end = index + 1; end < N && mHashes[end] == hash; end++) {
        if (key.equals(mArray[end << 1])) return end;
    }

    // Search for a matching key before the index.
    for (int i = index - 1; i >= 0 && mHashes[i] == hash; i--) {
        if (key.equals(mArray[i << 1])) return i;
    }

    // Key not found -- return negative value indicating where a
    // new entry for this key should go.  We use the end of the
    // hash chain to reduce the number of array entries that will
    // need to be copied when inserting.
    return ~end;
}
```



## ArraySet

`ArraySet`中提供两个数组`mHashes`和`mArray`分别存储`hash`值和`value`值。因为不需要存储`key`所以两个数组的长度是一样的。


## SparseArray

`SparseArray`的`key`是`int`类型的，所以`key`和`hash`值相同。所以不用再存储`key`了。两个数组长度也是一样的。


## **参考**

* [ArrayMap](http://gityuan.com/2019/01/13/arraymap/)

