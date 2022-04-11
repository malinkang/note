
## 第34条：用enum代替int常量

在编程语言中还没有引入枚举类型之前，表示枚举类型的常量模式是声明一组具名的int常量，每个类型成员一个常量：

```java
public static final int APPLE_FUJI = 0;public static final int APPLE_PIPPIN = 1;public static final int APPLE_GRANNY_SMITH = 2;public static final int ORANGE_NAVEL = 0;public static final int ORANGE_TEMPLE = 1;public static final int ORANGE_BLOOD = 2;
```

这种方法称作`int枚举模式`。在这种模式中使用`String`常量，而不是`int`常量。这样的变体被称为`String枚举模式`。

`Java 1.5`增加了枚举类型，可以避免`int`和`String`枚举模式的缺点。

```java
public enum Apple {FUJI, PIPPIN, GRANNY_SMITH}public enum ORANGE {NAVEL, TEMPLE, BLOOD}
```

举个枚举类型的好例子：

```java
public enum Planet {    MERCURY(3.302e+23, 2.439e6),    VENUS  (4.869e+24, 6.052e6),    EARTH  (5.975e+24, 6.378e6),    MARS   (6.419e+23, 3.393e6),    JUPITER(1.899e+27, 7.149e7),    SATURN (5.685e+26, 6.027e7),    URANUS (8.683e+25, 2.556e7),    NEPTUNE(1.024e+26, 2.477e7);    private final double mass;           // In kilograms    private final double radius;         // In meters    private final double surfaceGravity; // In m / s^2    // Universal gravitational constant in m^3 / kg s^2    private static final double G = 6.67300E-11;    // Constructor    Planet(double mass, double radius) {        this.mass = mass;        this.radius = radius;        surfaceGravity = G * mass / (radius * radius);    }    public double mass()           { return mass; }    public double radius()         { return radius; }    public double surfaceGravity() { return surfaceGravity; }    public double surfaceWeight(double mass) {        return mass * surfaceGravity;  // F = ma    }}
```

下面是一个简短的程序，根据某个物体在地球上的重量，打印出该物体在所有8颗行星上的重量：

```java
// Takes earth-weight and prints table of weights on all planets (Page 160)public class WeightTable {   public static void main(String[] args) {      double earthWeight = Double.parseDouble(args[0]);      double mass = earthWeight / Planet.EARTH.surfaceGravity();      for (Planet p : Planet.values())         System.out.printf("Weight on %s is %f%n",                 p, p.surfaceWeight(mass));   }}
```

每个`Plant`常量都关联了不同的数据，但你有时需要将本质上不同的行为与每个常量关联起来。


## 第35条：用实例域代替序数

许多枚举天生就与一个单独的int值相关联。所有的枚举都有一个ordinal方法，它返回每个枚举常量在类型中的数字位置。你可以试着从序数中得到关联的int值。

```java
public enum Ensemble {    SOLO, DUET, TRIO, QUARTET, QUINTET,    SEXTET, SEPTET, OCTET, NONET, DECTET;    public int numberOfMusicians() {        return ordinal() + 1;    }}
```

虽然这个枚举不错，但是维护起来就像一场噩梦。如果常量进行重新排列，numberOfMusicians方法就会遭到破坏。如果要再添加一个与已经用过的int值关联的枚举常量，就没那么走运了。例如，给双四重奏（double quartet）添加一个常量，它就像个八重奏一样，是由8位演奏家组成，但是没有办法做到。

永远不要根据枚举的序数导出与它关联的值，而是要将它保存在一个实例域中：

```java
public enum Ensemble {    SOLO(1), DUET(2), TRIO(3), QUARTET(4), QUINTET(5),    SEXTET(6), SEPTET(7), OCTET(8), DOUBLE_QUARTET(8),    NONET(9), DECTET(10),TRIPLE_QUARTET(12);    private final int numberOfMusicians;    Ensemble(int size) {        this.numberOfMusicians = size;    }    public int numberOfMusicians() {        return numberOfMusicians;    }}
```

Enum规范中谈到ordinal时这么写道：“大多数程序要都不需要这个方法。它是设计成用于像`EnumSet`和`EnumMap`这种基于枚举的通用数据结构的。”除非你再编写的是这种数据结构，否则最好完全避免使用ordinal方法。


## 第36条：用EnumSet替代位域


## 第37条：用EnumMap替代序数索引


## 第38条：用接口模拟可伸缩的枚举


## 第39条：注解优先于命名模式


## 第40条：坚持使用Override注解


## 第41条：用标记接口定义类型

