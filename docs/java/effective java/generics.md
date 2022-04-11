
## 第26条：请不要在新代码中使用原生态类型

声明中具有一个或者多个`类型参数（type parameter）`的类或者接口就是泛型类或者接口。泛型类和接口统称为`泛型（generic type）`。

每种泛型定义一组参`数化的类型（parameterized type）`，构成格式为：先是类或者接口的名称，接着用尖括号（<>）把对应于泛型形式类型参数的实际类型参数列表括起来。

每个泛型都定义一个`原生态类型（raw type）`，即不带任何实际类型参数的泛型名称。例如，与`List<E>`相对应的原生态类型是`List`。原生态类型就像从类型声明中删除了所有泛型信息一样。

如果不提供类型参数，使用集合类型和其他泛型也仍然是合法的，但是不应该这么做。**如果使用原生态类型，就失掉了泛型在安全性和表述性方面的所有优势**。既然不应该使用原生态类型，为什么Java的设计者还要允许使用它们呢？这是为了提供兼容性。因为泛型出现的时候，已经存在大量没有使用泛型的Java代码。人们认为让所有这些代码保持合法，并且能够与使用泛型的新代码胡勇，这一点很重要。它必须合法，才能将参数化类型的实例传递给那些被设计成使用普通类型的方法，反之亦然。这种需求被称作`移植兼容性（Migration Compatibility）`，促成了支持原生态类型的决定。

不要在新代码中使用原生态类型，这条规则有两个小小的例外，两者都源于“泛型信息可以在运行时被擦除”这一事实。在`类字面量（class literal）`中必须使用原生态类型。`List.class`，`String[].class`和`int.class`都合法，但是`List<String>.class`和`List<?>.class`则不合法。

第二个例外与`instanceof`操作符有关。由于泛型信息可以在运行时被擦除，因此在参数化类型**而非无限制通配符类型**上使用`instanceof`操作符是非法的。用无限制通配符类型替代原生态类型，对`instanceof`操作符的行为不会产生任何影响。在这种情况下，尖括号和问好就显得多余。


## 第27条：消除非受检警告

在用泛型编程时，会遇到许多编译器警告：`非受检强制转化警告（unchecked cast warnings）`、非受检方法调用警告、非受检普通数组创建警告，以及`非受检转换警告（unchecked conversion warnings）`。

有许多非受检警告很容易消除。有些警告比较难以消除。如果无法消除警告，同时可以证明引起警告的代码是类型安全的，可以用`@SuppressWarnings("unchecked")`注解来禁止这条警告。

`SuppressWarnings`注解可以用在任何力度的级别中，从单独的局部变量声明到整个类都可以。应该始终在尽可能小的范围中使用`SuppressWarnings`注解。它通常是个变量声明，或是非常简短的方法或者构造器。永远不要在整个类上使用`SuppressWarnings`，这么做可能会掩盖了重要的警告。


## 第28条：列表优先于数组

数组与泛型相比，有两个重要的不同点。首先，数组是`协变的（covariant）`。表示如果`Sub`为`Super`的子类型，那么数组类型`Sub[]`就是`Super[]`的子类型。相反，泛型则是不可变的（invariant）：对于任意两个不同的类型`Type1`和`Type2`，List既不是List的子类型，也不是List的超类型。

```java
//运行时报错: java.lang.ArrayStoreException: java.lang.StringObject[] objectArray = new Long[1];objectArray[0] = "I don't fit in";//编译时出错:Incompatible typesList<Object> ol = new ArrayList<Long>(); //ol.add("I don't fit in");
```

数组与泛型之间的第二大区别在于，数组是`具体化的（reified）`。因此数组会在运行时才会知道并检查它们的元素类型约束。相比之下，泛型则是通过`擦除（erasure）`来实现的。因此泛型只在编译时强化它们的类型信息，并在运行时丢弃它们的元素类型信息。

由于上述这些根本的区别，因此数组和泛型不能很好地混合使用。例如，创建泛型、参数化类型或者类型参数的数组是非法的。这些数组创建表达式没有一个是合法的`new List<E>[]`、`new List<String>[]`和`new E[]`。这些在编译时都会导致一个`generic array creation`错误。

从技术的角度来书，像`E`、`List<E>`和`List<String>`这样的类型应称作不可具体化的（non-reifialbe）类型。直观地说，不可具体化的类型是指运行时表示法包含的信息比它的编译时表示法包含的信息更少的类型。唯一可具体化的（reifiable）参数化类型是无限制的通配符类型，如`List<?>`。虽然不常用，但是创建无限制通配类型的数组是合法的。


## 第29条：优先考虑泛型

```java
public class Stack<E> {    private E[] elements;    private int size = 0;    private static final int DEFAULT_INITIAL_CAPACITY = 16;    public Stack() {        //编译时错误 type parameter E cannot be instantiated directly        elements = new E[DEFAULT_INITIAL_CAPACITY];    }    public void push(E e) {        ensureCapacity();        elements[size++] = e;    }    public E pop() {        if (size == 0)            throw new EmptyStackException();        E result = elements[--size];        elements[size] = null;        return result;    }    public boolean isEmpty() {        return size == 0;    }    private void ensureCapacity() {        if (elements.length == size)            elements = Arrays.copyOf(elements, 2 * size + 1);    }}
```

不能创建不可具体化的类型的数组，解决这个问题有两种方法。第一种，直接绕过创建泛型数组的禁令：创建一个Object的数组，并将它转换成泛型数组类型。现在错误是消除了，但是编译器会产生一条警告。这种用法是合法的，但不是类型安全的。

```java
@SuppressWarnings("unchecked")public Stack() {    elements = (E[]) new Object[DEFAULT_INITIAL_CAPACITY];}
```

消除`Stack`中泛型数组创建错误的第二种方法是，将`elements`域的类型从`E[]`改成`Object[]`。

```java
public E pop() {    if (size == 0)        throw new EmptyStackException();    @SuppressWarnings("unchecked")    E result = (E) elements[--size];    elements[size] = null;    return result;}
```

具体选择这两种方法中的哪一种来处理泛型数组创建错误，则主要看个人的偏好了。所有其他的东西都一样，但是禁止数组类型的未受检转换比禁止标量类型（scalar type）更加危险，所以建议采用第二种方案。但是在比`Stack`更实际的泛型类中，或许代码中会有多个地方需要从数组中读取元素，因此选择第二种方案需要多次转换成E，这也是第一种方案之所以更常用的原因。


## 第30条：优先考虑泛型方法

就如类可以从泛型中受益一般，方法也一样。静态工具方法尤其适合泛型化。 `Collections`中的所有“算法”方法都泛型化了。

```java
public static <E> Set<E> union(Set<E> s1, Set<E> s2) {    Set<E> result = new HashSet<E>(s1);    result.addAll(s2);    return result;}
```

```java
public static void main(String[] args) {    Set<String> guys = new HashSet<>(Arrays.asList("Tom", "Dick", "Harry"));    Set<String> stooges = new HashSet<>(Arrays.asList("Larry", "Moe", "Curly"));    Set<String> aflCio = union(guys,stooges);    System.out.println(aflCio); //[Moe, Tom, Harry, Larry, Curly, Dick]}
```


## 第31条：利用有限制通配符来提升API的灵活性

为`Stack`增加一个方法：

```java
public void pushAll(Iterable<E> src) {    for (E e : src)        push(e);}
```

```java
Stack<Number> numberStack = new Stack<>();Iterable<Integer> integers = new ArrayList<>();numberStack.pushAll(integers); //编译时错误
```

幸运的是，有一种解决办法。`Java`提供了一种特殊的参数化类型，称作`有限制的通配符类型（bounded wildcard type）`。修改pushAll来使用这个类型：

```java
public void pushAll(Iterable<? extends E> src) {    for (E e : src)        push(e);}
```

编写一个与`pushAll`方法相呼应的方法`popAll`：

```java
public void popAll(Collection<E> dst) {    while (!isEmpty())        dst.add(pop());}
```

```java
Stack<Number> numberStack = new Stack<>();Collection<Object> integers = new ArrayList<>();numberStack.popAll(integers); //编译时错误
```

如果试着用上述的`popAll`版本编译这段客户端代码，就会得到一个非常类似于第一次用`pushAll`时的错误。通配符类型同样提供了一种解决办法：

```java
public void popAll(Collection<? super E> dst) {    while (!isEmpty())        dst.add(pop());}
```

结论很明显。**为了获得最大限度的灵活性，要在表示生产者或者消费者的输入参数上使用通配符类型**。如果某个输入参数既是生产者，又是消费者，那么通配符类型对你就没有什么好处了：因为你需要的是严格的类型匹配，这是不用任何通配符而得到的。

下面的助记符便于让你记住要使用哪种通配符类型：

```
PECS 表示producer-extends，consumer-super
```

换句话说，如果参数化类型表示一个T生产者，就使用<? extends T>；如果它表示一个T消费者，就使用<? super T>。在我们的`Stack`示例中，pushAll的src参数产生E实例供Stack使用，因此src相应的类型为`Iterable<? extends E>`；popAll的dst参数通过Stack消费E实例，因此dst相应的类型为`Collection<? super E>`。PECS这个助记符突出了使用通配符类型的基本原则。


## 第33条：优先考虑类型安全的异构容器

泛型最常用于集合，如`Set`和`Map`。每个容器只能有固定数目的类型参数。一个Set只有一个类型参数，一个Map有两个类型参数。但是，有时候可能需要更多的灵活性。例如，数据库行可以有任意多的列，如果能以类型安全的方式访问所有列就好了。幸运的是，有一种方法可以很容易做到这一点。这种想法就是将键进行参数化而不是将容器参数化。然后将参数化的键提交给容器，来插入或者获取值。用泛型系统来确保值的类型与它的键相符。

```java
// Typesafe heterogeneous container pattern (Pages 151-4)public class Favorites {    private Map<Class<?>, Object> favorites = new HashMap<>();    public <T> void putFavorite(Class<T> type, T instance) {        favorites.put(Objects.requireNonNull(type), instance);    }    public <T> T getFavorite(Class<T> type) {        return type.cast(favorites.get(type));    }//    // Achieving runtime type safety with a dynamic cast//    public <T> void putFavorite(Class<T> type, T instance) {//        favorites.put(Objects.requireNonNull(type), type.cast(instance));//    }    public static void main(String[] args) {        Favorites f = new Favorites();        f.putFavorite(String.class, "Java");        f.putFavorite(Integer.class, 0xcafebabe);        f.putFavorite(Class.class, Favorites.class);        String favoriteString = f.getFavorite(String.class);        int favoriteInteger = f.getFavorite(Integer.class);        Class<?> favoriteClass = f.getFavorite(Class.class);        System.out.printf("%s %x %s%n", favoriteString,                favoriteInteger, favoriteClass.getName());    }}
```

`Favorites`实例是类型安全的：当你向它请求String的时候，它从来不会返回一个Integer给你。同时它也是异构的（heterogeneous）：不像普通的map，它的所有键都是不同类型的。因此，我们将`Favorites`称作类型安全的异构容器。

