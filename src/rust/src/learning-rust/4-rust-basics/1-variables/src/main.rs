fn main() {
//----------------------------------------------------------------
//常量定义（常量默认不能变，并且总是不能变。不允许对常量使用mut。）
    const ONE_HOUR_IN_SECONDS: u32 = 1 * 60 * 60;
    println!("const val = {}", ONE_HOUR_IN_SECONDS);

//变量和可变性
    //let x = 3;              //变量默认是不可改变的(immutable)
    let mut x = 3;        //变量可变(mutable)
    println!("x={}",x);

    x = 4;                  //改变不可变值，编译出错
    println!("now x={}",x);


//----------------------------------------------------------------
//变量的作用域
/*
    {           // < --- a的作用域这里开始
        let mut a = 1;
        println!("a = {}", a);
    }           // < --- a的作用域到这里结束
    a = 2;                     //编译出错，a没有定义
    println!("now a = {}", a); //编译出错，a没有定义
*/

    let mut a = 0; // < --- a的作用域这里开始
    println!("1 a={}",a);
    {
        a = 1;
        println!("2 a = {}", a);
    }
    println!("3  a = {}", a);  //编译正常

//----------------------------------------------------------------
//隐藏（Shadowing）
    let b = 5;
    let b = b + 1;
    {
        let b = b * 2;
        println!("b in the inner scope is: {}", b);
    }
    println!("b is: {}", b);

}

