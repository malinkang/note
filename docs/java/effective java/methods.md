
## 第49条：检查参数的有效性

对于公有的方法，要用Javadoc的`@throws`标签在文档中说明违反参数值会抛出的异常。一旦在文档中记录了对于方法参数的限制，并且记录了一旦违反这些限制将要抛出的异常，强加这些限制就是非常简单的事情了。

```java
 /**     * Returns a {@code BigInteger} whose value is {@code this mod m}. The     * modulus {@code m} must be positive. The result is guaranteed to be in the     * interval {@code [0, m)} (0 inclusive, m exclusive). The behavior of this     * function is not equivalent to the behavior of the % operator defined for     * the built-in {@code int}'s.     *     * @param m the modulus.     * @return {@code this mod m}.     * @throws NullPointerException if {@code m == null}.     * @throws ArithmeticException if {@code m < 0}.     */    public BigInteger mod(BigInteger m) {        if (m.signum() <= 0) {            throw new ArithmeticException("m.signum() <= 0");        }        return new BigInteger(BigInt.modulus(getBigInt(), m.getBigInt()));    }
```


## 第50条：必要时进行保护性拷贝


## 第51条：谨慎设计方法签名


## 第52条：慎用重载

下面的程序试图根据一个集合（collection）是Set、List，还是其他的集合类型，来对他们进行分类：

```java
public class CollectionClassifier {    public static String classify(Set<?> s) {        return "Set";    }    public static String classify(List<?> list) {        return "List";    }    public static String classify(Collection<?> list) {        return "Unknown Collection";    }    public static void main(String[] args) {        Collection<?>[] collections = {                new HashSet<String>(),                new ArrayList<BigInteger>(),                new HashMap<String, String>().values()        };        for (Collection<?> collection : collections) {            System.out.println(classify(collection));        }    }}
```

你可能期望这个程序会打印“Set”，紧接着是“List”，以及“Unknown Collection”，但实际上不是这样。它是打印“Unknown Collection”三次。因为`classify`方法被`重载（overloaded）`了，而要调用哪个重载方法是在编译时做出决定的。对于for循环中的全部三次迭代，参数的编译时类型都是相同的：Collection<?>。

对于重载方法（overloaded method）的选择是静态的，而对于被覆盖的方法（overridden method）的选择则是动态的。选择被覆盖的方法的正确版本是在运行时进行的，选择的依据是被调用方法所在对象的运行时类型。

```java
class Wine {    String name() {        return "wine";    }}class SparklingWine extends Wine {    @Override    String name() {        return "sparkling wine";    }}class Champagne extends SparklingWine {    @Override    String name() {        return "champagne";    }}public class Overriding {    public static void main(String[] args) {        Wine[] wines = {                new Wine(), new SparklingWine(), new Champagne()        };        for (Wine wine : wines) {            System.out.println(wine.name());        }    }}/*winesparkling winechampagne */
```

避免胡乱地使用重载机制。安全而饱受的策略是，永远不要导出两个具有相同参数数目的重载方法。如果方法使用可变参数（varargs），保守的策略是根本不要重载它。如果你遵守这些限制，永远也不会陷入到“对于任何一组实际的参数，哪个重载方法时适用的”这样的疑惑中。

在Java1.5发行版本之前，所有的基本类型都基本不同于所有的引用类型，但是当自动装箱出现之后，就不再如此了。

```java
public class SetList {    public static void main(String[] args) {        Set<Integer> set = new TreeSet<>();        List<Integer> list = new ArrayList<>();        for (int i = -3; i < 3; i++) {            set.add(i);            list.add(i);        }        for (int i = 0; i < 3; i++) {            set.remove(i);            list.remove(i);        }        System.out.println(set + " " + list); //[-3, -2, -1] [-2, 0, 2]    }}
```

`set.remove(i)`调用选择重载方法`remove(E)`，这里的E是集合（Integer）的元素类型，将i从int自动装箱到Integer中。`list.remove(i)`调用选择重载方法`remove(int i)`，它从列表的指定位置上去除元素。

```java
for (int i = 0; i < 3; i++) {    set.remove(i);    list.remove((Integer) i);}System.out.println(set + " " + list); //[-3, -2, -1] [-3, -2, -1]
```


## 第53条：慎用可变参数


## 第54条：返回零长度的数组或者集合，而不是null


## 第55条：为所有到处的API元素编写文档注释

