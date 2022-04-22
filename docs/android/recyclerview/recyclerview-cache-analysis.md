上一篇分析`RecyclerView`整体流程的时候提到，`RecyclerView`缓存机制比较复杂，所以这一篇单独分析一下`RecyclerView`的缓存机制。


## Recycler中的缓存

`Recycler`中定义了三个list来缓存`ViewHolder`，那这几个缓存有什么区别呢。

我们先来看`mAttachedScrap`和`mChangedScrap`。`Recycler`的`scrapView`中调用`mAttachedScrap`和`mChangedScrap`的`add`方法。

```java
//LayoutManager的scrapOrRecycleView方法
private void scrapOrRecycleView(Recycler recycler, int index, View view) {
    final ViewHolder viewHolder = getChildViewHolderInt(view);
    if (viewHolder.shouldIgnore()) {
        if (DEBUG) {
            Log.d(TAG, "ignoring view " + viewHolder);
        }
        return;
    }
    if (viewHolder.isInvalid() && !viewHolder.isRemoved()
            && !mRecyclerView.mAdapter.hasStableIds()) {
        removeViewAt(index);
        recycler.recycleViewHolderInternal(viewHolder);
    } else {
        detachViewAt(index);
        //调用Recycler的scrapView的方法
        recycler.scrapView(view);
        mRecyclerView.mViewInfoStore.onViewDetached(viewHolder);
    }
}
//LayoutManager的detachAndScrapAttachedViews方法
public void detachAndScrapAttachedViews(@NonNull Recycler recycler) {
    final int childCount = getChildCount();
    for (int i = childCount - 1; i >= 0; i--) {
        final View v = getChildAt(i);

        scrapOrRecycleView(recycler, i, v);
    }
}
```

在`detachAndScrapAttachedViews`方法中可以看到RecyclerView中的所有Child也就是屏幕中的所有View都被添加到`mAttachedScrap`中。`detachAndScrapAttachedViews`被`onLayoutChildren`方法调用。

所以当我们调用`adapter`的`notifyDataSetChanged`方法时会调用`requestLayout`触发`onLayout`，然后会回收屏幕中所有的`holder`。再次获取时复用这些`holder`。

```java
//RecyclerViewDataObserver onChanged方法
@Override
public void onChanged() {
    assertNotInLayoutOrScroll(null);
    mState.mStructureChanged = true;

    processDataSetCompletelyChanged(true);
    if (!mAdapterHelper.hasPendingUpdates()) {
        requestLayout();
    }
}
```

`mCacheViews`用于存放哪些缓存呢，我们同样可以查看`mCacheViews`的`add`方法调用位置，以及一系列的调用链

```java
/**
* Remove a child view and recycle it using the given Recycler.
*
* @param index    Index of child to remove and recycle
* @param recycler Recycler to use to recycle child
*/
public void removeAndRecycleViewAt(int index, @NonNull Recycler recycler) {
    final View view = getChildAt(index);
    removeViewAt(index);
    recycler.recycleView(view);
}
//LinearLayoutManager的recycleChildren方法
private void recycleChildren(RecyclerView.Recycler recycler, int startIndex, int endIndex) {
    if (startIndex == endIndex) {
        return;
    }
    if (DEBUG) {
        Log.d(TAG, "Recycling " + Math.abs(startIndex - endIndex) + " items");
    }
    if (endIndex > startIndex) {
        for (int i = endIndex - 1; i >= startIndex; i--) {
            removeAndRecycleViewAt(i, recycler);
        }
    } else {
        for (int i = startIndex; i > endIndex; i--) {
            removeAndRecycleViewAt(i, recycler);
        }
    }
}
//LinearLayoutManager的recycleViewsFromStart方法
//recycleViewsFromStart 和 recycleViewsFromEnd两个方法其实差不多只不过开始回收的位置不一样
//如果向上滑动会调用recycleViewsFromStart 优先回收底部的view，如果向下滑动则相反
private void recycleViewsFromStart(RecyclerView.Recycler recycler, int scrollingOffset,
        int noRecycleSpace) {
    if (scrollingOffset < 0) {
        if (DEBUG) {
            Log.d(TAG, "Called recycle from start with a negative value. This might happen"
                    + " during layout changes but may be sign of a bug");
        }
        return;
    }
    // ignore padding, ViewGroup may not clip children.
    final int limit = scrollingOffset - noRecycleSpace;
    final int childCount = getChildCount();
    if (mShouldReverseLayout) {
        for (int i = childCount - 1; i >= 0; i--) {
            View child = getChildAt(i);
            //这是是判断是否可见来回收
            if (mOrientationHelper.getDecoratedEnd(child) > limit
                    || mOrientationHelper.getTransformedEndWithDecoration(child) > limit) {
                // stop here
                recycleChildren(recycler, childCount - 1, i);
                return;
            }
        }
    } else {
        for (int i = 0; i < childCount; i++) {
            View child = getChildAt(i);
            if (mOrientationHelper.getDecoratedEnd(child) > limit
                    || mOrientationHelper.getTransformedEndWithDecoration(child) > limit) {
                // stop here
                recycleChildren(recycler, 0, i);
                return;
            }
        }
    }
}
private void recycleByLayoutState(RecyclerView.Recycler recycler, LayoutState layoutState) {
    if (!layoutState.mRecycle || layoutState.mInfinite) {
        return;
    }
    int scrollingOffset = layoutState.mScrollingOffset;
    int noRecycleSpace = layoutState.mNoRecycleSpace;
    if (layoutState.mLayoutDirection == LayoutState.LAYOUT_START) {
        recycleViewsFromEnd(recycler, scrollingOffset, noRecycleSpace);
    } else {
        recycleViewsFromStart(recycler, scrollingOffset, noRecycleSpace);
    }
}
```

`recycleByLayoutState`会被`fill`方法调用。除了`onLayoutChildren`方法会调用`fill`方法之外，`scrollBy`也会调用。在滑动过程中，会判断该View是否可见，如果不可见，则会判断`mCacheViews`是否已经达到最大容量。如果没达到直接添加。 如果已经满了，则会移除第一条，并把移除的添加到`RecycledViewPool`里面，再进行添加。


## 获取缓存

`tryGetViewHolderForPositionByDeadline`方法会依次尝试`从mAttachedScrap`、`mCachedViews`和`RecycledViewPool`中获取`ViewHolder`。

```java
@Nullable
ViewHolder tryGetViewHolderForPositionByDeadline(int position,
        boolean dryRun, long deadlineNs) {
    if (position < 0 || position >= mState.getItemCount()) {
        throw new IndexOutOfBoundsException("Invalid item position " + position
                + "(" + position + "). Item count:" + mState.getItemCount()
                + exceptionLabel());
    }
    boolean fromScrapOrHiddenOrCache = false;
    ViewHolder holder = null;
    // 0) If there is a changed scrap, try to find from there
    //首先先从 changed scrap 中获取
    if (mState.isPreLayout()) {
        holder = getChangedScrapViewForPosition(position);
        fromScrapOrHiddenOrCache = holder != null;
    }
    // 1) Find by position from scrap/hidden list/cache
    //通过position 从scrap/hidden list/cache中获取
    if (holder == null) {
        holder = getScrapOrHiddenOrCachedHolderForPosition(position, dryRun);
        if (holder != null) {
            if (!validateViewHolderForOffsetPosition(holder)) {
                // recycle holder (and unscrap if relevant) since it can't be used
                if (!dryRun) {
                    // we would like to recycle this but need to make sure it is not used by
                    // animation logic etc.
                    holder.addFlags(ViewHolder.FLAG_INVALID);
                    if (holder.isScrap()) {
                        removeDetachedView(holder.itemView, false);
                        holder.unScrap();
                    } else if (holder.wasReturnedFromScrap()) {
                        holder.clearReturnedFromScrapFlag();
                    }
                    recycleViewHolderInternal(holder);
                }
                holder = null;
            } else {
                fromScrapOrHiddenOrCache = true;
            }
        }
    }
    if (holder == null) {
        final int offsetPosition = mAdapterHelper.findPositionOffset(position);
        if (offsetPosition < 0 || offsetPosition >= mAdapter.getItemCount()) {
            throw new IndexOutOfBoundsException("Inconsistency detected. Invalid item "
                    + "position " + position + "(offset:" + offsetPosition + ")."
                    + "state:" + mState.getItemCount() + exceptionLabel());
        }

        final int type = mAdapter.getItemViewType(offsetPosition);
        // 2) Find from scrap/cache via stable ids, if exists
        //通过 stable id从 scrap/cache中获取
        if (mAdapter.hasStableIds()) {
            holder = getScrapOrCachedViewForId(mAdapter.getItemId(offsetPosition),
                    type, dryRun);
            if (holder != null) {
                // update position
                holder.mPosition = offsetPosition;
                fromScrapOrHiddenOrCache = true;
            }
        }
        if (holder == null && mViewCacheExtension != null) {
            // We are NOT sending the offsetPosition because LayoutManager does not
            // know it.
            final View view = mViewCacheExtension
                    .getViewForPositionAndType(this, position, type);
            if (view != null) {
                holder = getChildViewHolder(view);
                if (holder == null) {
                    throw new IllegalArgumentException("getViewForPositionAndType returned"
                            + " a view which does not have a ViewHolder"
                            + exceptionLabel());
                } else if (holder.shouldIgnore()) {
                    throw new IllegalArgumentException("getViewForPositionAndType returned"
                            + " a view that is ignored. You must call stopIgnoring before"
                            + " returning this view." + exceptionLabel());
                }
            }
        }
        //尝试从RecycledViewPool中获取
        if (holder == null) { // fallback to pool
            if (DEBUG) {
                Log.d(TAG, "tryGetViewHolderForPositionByDeadline("
                        + position + ") fetching from shared pool");
            }
            holder = getRecycledViewPool().getRecycledView(type);
            if (holder != null) {
                holder.resetInternal();
                if (FORCE_INVALIDATE_DISPLAY_LIST) {
                    invalidateDisplayListInt(holder);
                }
            }
        }
        if (holder == null) {
            long start = getNanoTime();
            if (deadlineNs != FOREVER_NS
                    && !mRecyclerPool.willCreateInTime(type, start, deadlineNs)) {
                // abort - we have a deadline we can't meet
                return null;
            }
            //都没有获取到
            //创建viewholder
            holder = mAdapter.createViewHolder(RecyclerView.this, type);
            if (ALLOW_THREAD_GAP_WORK) {
                // only bother finding nested RV if prefetching
                RecyclerView innerView = findNestedRecyclerView(holder.itemView);
                if (innerView != null) {
                    holder.mNestedRecyclerView = new WeakReference<>(innerView);
                }
            }

            long end = getNanoTime();
            mRecyclerPool.factorInCreateTime(type, end - start);

        }
    }
    //...
    return holder;
}
```


## 缓存图解

上面已经分析了缓存个整个流程，为了更加直观，我做了几张图来梳理从进入列表，以及滑动过程中`Adapter`、`Recycler`以及`RecycledViewPool`是如何工作的。

![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/719f485c-4139-490b-8108-f9b329b5c19f/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083041Z&X-Amz-Expires=3600&X-Amz-Signature=8ada45560698c44ca32102f194c22518a30fe88d4b5e71cd3b86996460941d9a&X-Amz-SignedHeaders=host&x-id=GetObject)
![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/de87e2ad-222d-4f51-97a0-252cb2620a85/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083041Z&X-Amz-Expires=3600&X-Amz-Signature=62056399840d7795bb6b2f9a4f3f63f47fa331ebc4d5cb55dc7084ffec8a056b&X-Amz-SignedHeaders=host&x-id=GetObject)
滑动过程中`GapWorker`会多次调用`prefetchPositionWithDeadline()`方法。第一次缓存取不到缓存，调用`Adapter`的`createViewHolder()`，第二次会从缓存中，然后根据判断不可见，再存入缓存中。

![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/2a10ed88-f1cf-4076-b91b-a4f2a3762a3c/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083042Z&X-Amz-Expires=3600&X-Amz-Signature=b9e919e88e72198d9a58cb8a7b72886c571b48b3b3fbd10a4b58bb98bca9bf3f&X-Amz-SignedHeaders=host&x-id=GetObject)
![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/755c3dd1-95dd-45ae-b9b7-a4e41fec7cfd/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083041Z&X-Amz-Expires=3600&X-Amz-Signature=065442bbbca6b8a0b8cd63703e401ade065ec85cc341863c1db7bb985e1b11ff&X-Amz-SignedHeaders=host&x-id=GetObject)
![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/199dad6b-2020-4609-8042-953271494dda/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083041Z&X-Amz-Expires=3600&X-Amz-Signature=507efb58c1874a9a7ebd35e230bdad5290ec001f84d50b5ad6c2627a0c0b3527&X-Amz-SignedHeaders=host&x-id=GetObject)
![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/aa15890f-83c7-4c20-9822-17a7c6b31f79/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083042Z&X-Amz-Expires=3600&X-Amz-Signature=fd0476b35707fb19f20b7b9e5f389c54f57e40e41a99485718f1fc57297c9f65&X-Amz-SignedHeaders=host&x-id=GetObject)
![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/6b3a1f18-d5ef-4238-961a-3a6f8d806c08/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083042Z&X-Amz-Expires=3600&X-Amz-Signature=753eeb4faa18f00ae145cf5a144d1f5a462a9eb0baa6c0cd81ff33860b021202&X-Amz-SignedHeaders=host&x-id=GetObject)
![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/52ca7488-e920-4a0a-a9f3-ad126d593e33/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083042Z&X-Amz-Expires=3600&X-Amz-Signature=ed827165d4f060ca983d6cb023d074caa0ba95f48eca1c08764b73fa3bd5c89b&X-Amz-SignedHeaders=host&x-id=GetObject)
![](https://s3.us-west-2.amazonaws.com/secure.notion-static.com/ad9e7246-032d-42c2-919e-8df138f328ce/Untitled.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20220422%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20220422T083042Z&X-Amz-Expires=3600&X-Amz-Signature=d79ad2c409b6cc3d748ca570779830d67d20445da501a64f2089070dc217b38e&X-Amz-SignedHeaders=host&x-id=GetObject)

