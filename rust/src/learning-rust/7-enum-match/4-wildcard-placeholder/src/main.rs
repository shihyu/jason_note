#[derive(Debug)]
#[allow(dead_code)]
enum Month {
    Jan,
    Feb,
    Mar,
    Apr,
    May,
    Jun,
    Jul,
    Aug,
    Sep,
    Oct,
    Nov,
    Dec,
}
fn month_name_to_num(m: Month) {
    match m {
        Month::Jan => println!("1"),
        Month::Feb => println!("2"),
        Month::Mar => println!("3"),
        other => println!("other month, {:?}",other),
    } 
}
/*必须将通配分支放在最后!
 * 因为模式是按顺序匹配的，如果在通配分支后添加其他分支，
 * 通配分支后的分支永远不会被匹配到
 */
fn month_name_to_num2(m: Month) {
    match m {
        Month::Jan => println!("1"),
        Month::Feb => println!("2"),
        other => println!("other month, {:?}",other),
        Month::Mar => println!("3"),
    } 
}
fn month_name_to_num3(m: Month) {
    match m {
        Month::Jan => println!("1"),
        Month::Feb => println!("2"),
        _ => println!("other month"),
    } 
}

fn main() {
    month_name_to_num(Month::Jan);
    month_name_to_num(Month::Dec);

    month_name_to_num2(Month::Mar);
    month_name_to_num3(Month::Mar);
}











