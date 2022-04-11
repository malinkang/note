
## 第42条：Lambda优先于匿名类

```java
Collections.sort(words, new Comparator<String>() {    @Override    public int compare(String s1, String s2) {        return Integer.compare(s1.length(),s2.length());    }});
```

在`Java 8`中，带有单个抽象方法的接口被称作`函数接口（function interface）`。`Java`允许利用`Lambda`表达式创建这些接口的实例。`Lambda`表达式类似于匿名类的函数，但是比它简洁的多。

```
Collections.sort(words, (s1, s2) -> Integer.compare(s1.length(),s2.length()));
```

可以用`Lambda`表达式代替比较器构造方法(comparator construction method)

```
Collections.sort(words, Comparator.comparingInt(String::length));
```

利用`Java 8`在`List`接口中添加的`sort`方法，代码片段可以更加简短一些：

```java
words.sort(Comparator.comparingInt(String::length));
```

`Java`中增加了`Lambda`之后，使得之前不能使用函数对象的地方现在也能使用了。

```java
public enum Operation {    PLUS("+"){        @Override        public double apply(double x, double y) {            return x + y;        }    },    MINUS("-"){        @Override        public double apply(double x, double y) {            return x - y;        }    },    TIMES("*"){        @Override        public double apply(double x, double y) {            return x * y;        }    },    DIVIDE("/"){        @Override        public double apply(double x, double y) {            return x / y;        }    };    private final String symbol;    Operation(String symbol){        this.symbol = symbol;    }    public abstract double apply(double x,double y);}
```

```java
public enum Operation {    PLUS("+", (x, y) -> x + y),    MINUS("-", (x, y) -> x - y),    TIMES("*", (x, y) -> x * y),    DIVIDE("/", (x, y) -> x / y);    private final String symbol;    private final DoubleBinaryOperator op;    Operation(String symbol, DoubleBinaryOperator op) {        this.symbol = symbol;        this.op = op;    }    public double apply(double x, double y) {        return op.applyAsDouble(x, y);    }}
```

`Lambda`限于函数接口，无法为带有多个抽象方法的接口创建实例。`Lambda`无法获得对自身的引用。在`Lambda`中，关键字`this`是指外围实例。在匿名类中，关键字`this`是指匿名类实例。如果需要从函数对象的主体内部访问它，就必须使用匿名类。


## 第43条：方法引用优先于Lambda

与匿名类相比，`Lambda`的主要优势在于更加简洁。`Java`提供了生成比`Lambda`更简洁的函数对象的方法：`方法引用(method reference)`。

```
Map<String,Integer> map = new HashMap<>();
System.out.println(map.merge("one",1,(oldValue,value)->oldValue + value));//1
System.out.println(map.merge("one",1,(oldValue,value)->oldValue + value));//2
```

`merge`方法时`Java 8`在`Map`接口中添加的。如果指定的键没有值，就会插入指定的值；如果值存在，`merge`方法就会将指定的函数应用到当期值和指定值上，并用结果覆盖当前值。

从`Java 8`开始，`Integer`提供了一个名为`sum`的静态方法，它的作用也同样是求和。我们只要传入一个对该方法的引用，就可以更轻松地得到相同的结果：

```
Map<String,Integer> map = new HashMap<>();
System.out.println(map.merge("one",1, Integer::sum));//1
System.out.println(map.merge("one",1, Integer::sum));//2
```


## 第44条：坚持使用标准的函数接口


## 第45条：谨慎使用 Stream


## 第46条：优先选择 Stream 中无副作用的函数


## 第47条：Stream 要优先用 Collection 作为返回类型


## 第48条：谨慎使用 Stream 并行

