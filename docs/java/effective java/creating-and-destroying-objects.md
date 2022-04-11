
## 第1条：考虑用静态工厂方法替代构造器

创建类实例最常用的方法就是提供一个公有的构造器。此外，还可以提供一个公有的`静态工厂方法（static factory method）`，它只是一个返回类的实例的静态方法。

```java
//来自Boolean的简单示例//这个方法将boolean基本类型值转换成了一个Boolean对象引用：public static Boolean valueOf(boolean b) {    return b ? TRUE : FALSE;}
```

**静态工厂方法与构造器不同的第一大优势在于，它们有名称。**

**静态工厂方法与构造器不同的第二大优势在于，不必在每次调用它们的时候都创建一个新对象。**这使得不可变类可以使用预先构建好的实例，或者将构件号的实例缓存起来，进行重复利用，从而避免创建不必要的重复对象。

**静态工厂方法与构造器不同的第三大优势在于，它们可以返回原返回类型的任何子类型的对象。**

**仅提供静态工厂方法的主要限制是没有公共或受保护构造函数的类不能被子类化。**

**静态工厂方法的第二个缺点是程序员很难找到它们。**在API文档中，它们没有像构造器那样在API文档中明确标识出来，因此，对于提供了静态工厂方法而不是构造器的类来说，要想查明如何实例化一个类，这是非常困难的。

静态工厂方法的一些惯用名称：

* from

```java
Date date = Date.from(instant);
```

* of

* valueOf：该方法返回的实例与它的参数具有相同的值。这样的静态工厂方法实际上是类型转换方法。

```java
public static String valueOf(int i) {    return Integer.toString(i);}
```

* instance或者getInstance

* create 或 newInstance

* getType

* newType

* type


## 第2条：遇到多个构造器参数时要考虑用构建器

静态工厂和构造器有个共同的局限性：它们都不能很好地扩展到大量的可选参数。考虑用一个类表示食品外面显示的营养成分标签。这些标签中有几个域是必需的：每份的含量、每罐的含量以及每份的卡路里，还有超过20个可选域：总脂肪量、饱和脂肪量、转化脂肪、胆固醇、钠等等。大多数产品在某几个可选域中都会有非零的值。

对于这样的类，程序员一向习惯采用**重叠构造器（telescoping constructor）**模式。

```java
public class NutritionFacts {    private final int servingSize; //必选    private final int servings; //必选    private final int calories;//可选    private final int fat; //可选    private final int sodium; //可选    private final int carbohydrate; //可选    public NutritionFacts(int servingSize, int servings) {        this(servingSize, servings, 0);    }    public NutritionFacts(int servingSize, int servings, int calories) {        this(servingSize, servings, calories, 0);    }    public NutritionFacts(int servingSize, int servings, int calories, int fat) {        this(servingSize, servings, calories, fat, 0);    }    public NutritionFacts(int servingSize, int servings, int calories, int fat, int sodium) {        this(servingSize, servings, calories, fat, sodium, 0);    }    public NutritionFacts(int servingSize, int servings, int calories, int fat, int sodium, int carbohydrate) {        this.servingSize = servingSize;        this.servings = servings;        this.calories = calories;        this.fat = fat;        this.sodium = sodium;        this.carbohydrate = carbohydrate;    }}
```

**重叠构造器模式可行，但是当有许多参数的时候，客户端代码会很难编写，并且仍然较难以阅读**。

遇到许多构造器参数的时候，还有第二种替代方法，即`JavaBeans`模式。在这种模式下，调用一个无参构造器来创建对象，然后调用`setter`方法来设置每个必要的参数，以及每个相关的可选参数：

```java
public class NutritionFacts {    private  int servingSize; //必选    private  int servings; //必选    private  int calories;//可选    private  int fat; //可选    private  int sodium; //可选    private  int carbohydrate; //可选    public void setServingSize(int servingSize) {        this.servingSize = servingSize;    }    public void setServings(int servings) {        this.servings = servings;    }    public void setCalories(int calories) {        this.calories = calories;    }    public void setFat(int fat) {        this.fat = fat;    }    public void setSodium(int sodium) {        this.sodium = sodium;    }    public void setCarbohydrate(int carbohydrate) {        this.carbohydrate = carbohydrate;    }}
```

```java
NutritionFacts cocaCola = new NutritionFacts();cocaCola.setServingSize(240);cocaCola.setServings(8);cocaCola.setCalories(100);cocaCola.setSodium(35);cocaCola.setCarbohydrate(27);
```

遗憾的是，`JavaBeans`模式自身有着很严重的缺点。因为构造过程被分到了几个调用中，在构造过程中`JavaBean`可能处于不一致的状态。另一点不足在于，`JavaBeans`模式阻止了把类做成不可变的可能。

第三种替代方法`Builder`模式，既能保证像重叠构造器模式那样的安全性，也能保证像`JavaBeans`模式那么好的可读性。

```java
public class NutritionFacts {    private final int servingSize; //必选    private final int servings; //必选    private final int calories;//可选    private final int fat; //可选    private final int sodium; //可选    private final int carbohydrate; //可选    public static class Builder {        //必选参数        private final int servingSize;        private final int servings;        //可选参数        private int calories = 0;//可选        private int fat = 0; //可选        private int sodium = 0; //可选        private int carbohydrate = 0; //可选        public Builder(int servingSize, int servings) {            this.servingSize = servingSize;            this.servings = servings;        }        public Builder calories(int val) {            calories = val;            return this;        }        public Builder fat(int val) {            fat = val;            return this;        }        public Builder sodium(int val) {            sodium = val;            return this;        }        public Builder carbohydrate(int val) {            carbohydrate = val;            return this;        }        public NutritionFacts build() {            return new NutritionFacts(this);        }    }    private NutritionFacts(Builder builder) {        servingSize = builder.servingSize;        servings = builder.servings;        calories = builder.calories;        fat = builder.fat;        sodium = builder.sodium;        carbohydrate = builder.carbohydrate;    }}
```

调用

```java
 NutritionFacts cocaCola = new Builder(240, 8)                .calories(100).sodium(35).carbohydrate(27).build();
```

`Builder`模式也有自身的不足。为了创建对象，必须先创建它的构造器。虽然创建构造器的开销在实践中可能不那么明显，但是在某些时分注重性能的情况下，可能就成问题了。`Builder`模式还比重叠构造器模式更加冗长，因此它只在有很多参数的时候才使用。

简而言之，如果类的构造器或者静态工厂具有多个参数，设计这种类时，`Builder`模式就是种不错的选择，特别是当大多数参数都是可选的时候。与使用传统的重叠构造器模式相比，使用`Builder`的客户端代码将更易于阅读和编写，构建起也比`JavaBeans`更加安全。


## 第3条：用私有构造器或者枚举类型强化Singleton属性

`Signleton`指仅仅被实例化一次的类。`Singleton`通常被用来代表那些本质上唯一的系统组件，比如窗口管理器或者文件系统。当类成为`Singleton`会使它的客户端测试变得十分困难，因为无法给`Singleton`替换模拟实现，除非它实现一个充当其类型的接口。

在`Java 1.5`发行版本之前，实现`Singleton`有两种方法：

```java
public class Elvis {    public static final Elvis INSTANCE = new Elvis();    private Elvis() {}    public void leaveTheBuilding() {}}
```

在实现`Singleton`的第二种方法中，公有的成员是个静态工厂方法：

```java
public class Elvis {    private static final Elvis INSTANCE = new Elvis();    public static Elvis getInstance() {        return INSTANCE;    }    private Elvis() {}    public void leaveTheBuilding() {}}
```

从`Java 1.5`发型版本起，实现`Singleton`还有第三种方法。只需编写一个包含单个元素的枚举类型。

```java
public enum Elvis {    INSTANCE;    public void leaveTheBuilding(){}}
```

这种方法在功能上与公有域方法相近，但是它更加简洁，无偿地提供了序列化机制，绝对防止多次序列化，即使是在面对复杂的序列化或者反射攻击的时候。虽然这种方法还没有广泛采用，但是单元素的枚举类型已经成为实现Singleton的最佳方法。


## 第4条：通过私有构造器强化不可实例化的能力

有时候，你可能需要编写只包含静态方法和静态域的类。这些类的名声很不好，因为有些人在面向对象的语言中滥用这样的类来编写过程化的程序。尽管如此，它们也确实有它们特有的用处。我们可以利用这种类，以`java.lang.Math`或者`java.lang.Arrays`的方法，把基本类型的值或者数组类型上的相关方法组织起来。我们也可以通过`java.util.Collection`的方式，把实现特定接口的对象上的静态方法组织起来。最后，还可以利用这种类把final类上的方法组织起来，以取代扩展该类的做法。

这样的工具类（utility class）不希望被实例化，实例化它没有任何意义。然而，在缺少显式构造器的情况下，编译器会自动提供一个公有的、无参的缺省构造器（default constructor）。对于用户而言，这个构造器与其他的构造器没有任何区别。在已发行的API中常常可以看到一些被无意识地实例化的类。

```java
public class UtilityClass {    private UtilityClass(){        throw new AssertionError();    }}
```


## 第5条：避免创建不必要的对象

一般来说，最好能重用对象而不是在每次需要的时候就创建一个相同功能的新对象。重用方式既快速，又流行。如果对象是不可变的，它就始终可以被重用。

```java
//该语句每次被执行的时候都创建一个新的String实例String s = new String("stringette");
```

```java
String s = "stringette";
```

这个版本只用了一个`String`实例，而不是每次执行的时候都创建一个新的实例。而且，它可以保证，对于所有在同一台虚拟机中运行的代码，只要它们包含相同的字符串字面常量，该对象就会被重用。

除了重用不可变的对象之外，也可以重用那些已知不会被修改的可变对象。

```java
public class Person {    private final Date birthDate;    public Person(Date birthDate) {        this.birthDate = birthDate;    }    //检验这个人是否出生于1946年至1964年    public boolean isBabyBoomer() {        Calendar gmtCal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));        gmtCal.set(1946, Calendar.JANUARY, 1, 0, 0, 0);        Date boomStart = gmtCal.getTime();        gmtCal.set(1965, Calendar.JANUARY, 1, 0, 0, 0);        Date boomEnd = gmtCal.getTime();        return birthDate.compareTo(boomStart) >= 0 &&                birthDate.compareTo(boomEnd) < 0;    }}
```

`isBabyBoomer`每次被调用的时候，都会新建一个`Calendar`、一个`TimeZone`和两个`Date`实例，这是不必要的。下面的版本用一个静态的初始化器（initializer），避免了这种效率低下的情况：

```java
public class Person {    private final Date birthDate;    public Person(Date birthDate) {        this.birthDate = birthDate;    }    private static final Date BOOM_START;    private static final Date BOOM_END;    static {        Calendar gmtCal = Calendar.getInstance(TimeZone.getTimeZone("GMT"));        gmtCal.set(1946, Calendar.JANUARY, 1, 0, 0, 0);        BOOM_START = gmtCal.getTime();        gmtCal.set(1965, Calendar.JANUARY, 1, 0, 0, 0);        BOOM_END = gmtCal.getTime();    }    //检验这个人是否出生于1946年至1964年    public boolean isBabyBoomer() {        return birthDate.compareTo(BOOM_START) >= 0 &&                birthDate.compareTo(BOOM_END) < 0;    }}
```


## 第7条：消除过期的对象引用

```java
public class Stack {    private Object[] elements;    private int size = 0;    private static final int DEFAULT_INITIAL_CAPACITY = 16;    public Stack() {        elements = new Object[DEFAULT_INITIAL_CAPACITY];    }    public void push(Object e) {        ensureCapacity();        elements[size++] = e;    }    public Object pop() {        if (size == 0)            throw new EmptyStackException();        return elements[--size];    }    private void ensureCapacity() {        if (elements.length == size)            elements = Arrays.copyOf(elements, 2 * size + 1);    }}
```

如果一个栈先是增长，然后再收缩，那么，从栈中弹出来的对象将不会被当作垃圾回收，即使使用栈的程序不再引用这些对象，它们也不会被回收。这是因为，栈内部维护着对这些对象的`过期引用（obsolete reference）`。所谓的过期引用，是指永远也不会再被解除的引用。在本例中，凡是`elements`数组的“活动部分”之外的任何引用都是过期的。活动部分是指`elements`中下标小于`size`的那些元素。

这类问题的修复方法很简单：一旦对象引用已经过期，只需清空这些引用即可。

```java
public Object pop() {    if (size == 0)        throw new EmptyStackException();    Object result = elements[--size];    elements[size] = null;    return result;}
```


## 第8条：避免使用终结方法

终结方法通常是不可预测的，也是很危险的，一般情况下是不必要的。

