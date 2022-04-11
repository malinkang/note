
## 第57条：将局部变量的作用域最小化

要使局部变量的作用域最小化，最有力的方法就是在第一次使用它的地方声明。

循环中提供了特殊的机会来将变量的作用域最小化。for循环，都允许声明循环变量（loop variable），它们的作用域被限定在正好需要的范围之内。因此，如果在循环终止之后不再需要循环变量的内容，for循环就优于while循环。

```java
Iterator<Element> i = c.iterator();while(i.hasNext()){    doSomething(i.next());}Iterator<Element> i2 = c2.iterator();//本来要初始化一个新的循环变量i2，却使用了旧的循环变量i，i仍然在使用范围之内，代码可以通过编译//如果在for循环中，代码就根本不能通过编译。while(i.hasNext()){    doSomething(i2.next());}
```


## 第58条：for-each循环优于传统的for循环

在Java1.5发行版本之前，对集合进行遍历的首选做法如下：

```java
for (Iterator i = c.iterator();i.hasNext()) {    doSomething((Element)i.next());}
```

遍历数组的首选做法如下：

```java
for (int i = 0; i < a.length; i++){    doSomething(a[i]);}
```

这些做法都比`while`循环更好，但是它们也并不完美，迭代器和索引变量都会造成一些混乱。

`Java 1.5`发行版本中引入的`for-each`循环，通过完全隐藏迭代器或者索引变量，避免了混乱和出错的可能。

```java
for (Element e:elements){    doSomething(e);}
```

在对多个集合进行嵌套式迭代时，`for-each`循环相对于传统for循环的这种优势还会更加明显。

总之，for-each循环在简洁性和预防Bug方面有着传统的for循环无法比拟的优势，并且没有性能损失，应该尽可能地使用for-each循环。遗憾的是，有三种常见的情况无法使用for-each循环：


## 第59条：了解和使用类库

假设你希望产生位于0和某个上界之间的随机整数。面对这个常见的任务，可能会编写如下所示的方法：

```java
private static final Random rnd = new Random();static int random(int n) {    return Math.abs(rnd.nextInt()) % n;}
```

这个方法看起来可能不错，但是却有三个缺点。第一个缺点是，如果n是一个比较小的2的乘方，经过一段相当短的周期后，它产生的随机数序列将会重复。第二个缺点是，如果n比较大，这个缺点就会非常明显。

```java
public static void main(String[] args) {    int n = 2 * (Integer.MAX_VALUE / 3);    int low = 0;    for (int i = 0; i < 1000000; i++) {        if (random(n) < n / 2)            low++;    }    System.out.println(low);}
```

如果random方法工作正常的话，这个程序打印出来的数接近于一百万的一半，但是如果真正运行这个程序，就会发现它打印出来的数接近于666 666。由random方法产生的数字有2/3落在随机数取值范围的前半部分。

random方法的第三个缺点是，在极少数情况下，它的失败是灾难性的，返回一个落在指定范围之外的数。之所以如此，是因为这个方法试图通过调用Math.abs将rnd.nextInt()返回的值映射为一个非负证书int。如果nextInt()返回Integer.MIN_VALUE，那么


## 第60条：如果需要精确的答案，请避免使用float和double

`float`和`double`类型主要是为了科学计算和工程计算而设计的。它们执行`二进制浮点运算（binary floating-point arithmetic）`，这是为了在广泛的数值范围上提供较为精确的快速近似计算而精心设计的。然而，它们并没有提供完全精确的结果，所以不应该被用于需要精确结果的场合。**float和double类型尤其不适合用于货币计算**，因为要让一个float或者double精确地表示0.1是不可能的。

```java
System.out.println(1.03 - 0.42); //0.6100000000000001System.out.println(1.00 - 9 * 0.10); //0.09999999999999998
```

```java
double funds = 1.00;//口袋里有1美元钱int itemsBought = 0;//依次购买10美分、20美分...一直到1美元的糖果for (double price = 0.10; funds >= price; price += 0.10) {    funds -= price;    itemsBought++;}System.out.println(itemsBought + " items bought."); //3 items bought.System.out.println("Change:$" + funds); //Change:$0.3999999999999999
```

解决这个问题的正确方法是**使用BigDecimal、int或者long进行货币计算**。

```java
final BigDecimal TEN_CENTS = new BigDecimal(".10");int itemsBought = 0;BigDecimal funds = new BigDecimal("1.00");//口袋里有1元钱//依次购买10美分、20美分...一直到1美元的糖果for (BigDecimal price = TEN_CENTS; funds.compareTo(price)>=0; price =price.add(TEN_CENTS)) {    funds = funds.subtract(price);    itemsBought++;}System.out.println(itemsBought + " items bought."); //4 items bought.System.out.println("Money left over:$" + funds); //Money left over:$0.00
```

然而，使用BIgDecimal有两个缺点：与使用基本运算类型相比，这样做很不方便，而且速度很慢。

除了使用BigDecimal之外，还有一种办法是使用int或者long，到底选用int还是long要取决于所涉及数值的大小，同时要自己处理十进制小数点。

```java
int itemsBought = 0;int funds = 100;//口袋里有1元钱 以美分为单位//依次购买10美分、20美分...一直到1美元的糖果for (int price = 10; funds >= price; price += 10) {    funds -= price;    itemsBought++;}System.out.println(itemsBought + " items bought."); //4 items bought.System.out.println("Cash left over:$" + funds + " cents"); //Cash left over:$0 cents
```

总而言之，对于任何需要精度答案的计算任务，请不要使用float或者double。如果你想让系统来处理十进制小数点，并且不介意因为不使用基本类型而带来的不便，就请使用`BigDecimal`。使用`BigDecimal`还有一些额外的好处，它允许你完全控制舍入，每当一个操作涉及舍入的时候，你都可以从8种舍入模式中选择其一。如果你正通过合法强制的舍入行为进行商务计算，使用BigDecimal是非常方便的。如果性能非常关键，并且你又不介意自己处理十进制小数点，而且所涉及的数值又不太大，就可以使用int或者long。如果数值范围没有超过9位十进制数字，就可以使用int；如果不超过18位数字，就可以使用long。如果数值可能超过18位数字，就必须使用`BigDecimal`。


## 第61条：基本类型优先于装箱基本类型

Java有一个类型系统由两部分组成，它包含基本类型（primitive），如int、double和boolean，以及引用类型（reference type），如`String`和`List`。每个基本类型都有一个对应的引用类型，称作`装箱基本类型（boxed primitive）`。装箱基本类型中对应于int、double和boolean的分别是Integer、Double和Boolean。

在基本类型和装箱基本类型之间有三个主要区别。第一，基本类型只有值，而装箱基本类型则具有与它们的值不同的同一性。换句话说，两个装箱基本类型可以具有相同的值和不同的同一性。第二，基本类型只有函数值，而每个装箱基本类型则都有一个非函数值，除了它对应基本类型的所有函数值之外，还有个null。最后一点区别是，基本类型通常比装箱基本类型更节省时间和空间。

```java
//< 运算符导致自动拆箱 i==j 返回false所以 输出1//对装箱基本类型运用==操作符几乎总是错误的。Comparator<Integer> naturalOrder = (i, j) -> (i < j) ? -1 : (i == j ? 0 : 1);System.out.println(naturalOrder.compare(new Integer(42), new Integer(42))); //1
```

什么时候应该使用装箱基本类型呢？它们有几个合理的用处。第一个是作为集合中的元素、键和值。你不能将基本类型放在集合中，因此必须使用装箱基本类型。在参数化类型和方法中，必须使用装箱基本类型作为类型参数。最后，在进行反射的方法调用时，必须使用装箱基本类型。

总而言之，当可以选择的时候，基本类型要优先于装箱基本类型。基本类型更加简单，也更加快速。如果必须使用装箱类型，要特别小心！**自动装箱减少了使用装箱基本类型的繁琐性，但是并没有减小它的风险**。当程序用==操作符比较两个装箱基本类型时，它做了个同一性比较，这几乎肯定不是你所希望的。当程序进行设计装箱和拆箱基本类型的混合计算时，它会进行拆箱，当程序进行拆箱时，会抛出NullPointerException异常。最后，当程序装箱了基本类型值时，会导致较高的资源消耗和不必要的对象创建。


## 第62条：如果其他类型更适合，则尽量避免使用字符串


## 第63条：当心字符串连接的性能


## 第64条：通过接口引用对象


## 第65条：接口优先于反射机制


## 第66条：谨慎地使用本地方法


## 第67条：谨慎地进行优化


## 第68条：遵守普遍接受的命名管理

