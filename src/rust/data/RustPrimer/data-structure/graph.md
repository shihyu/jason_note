# 圖

## 圖的存儲結構

圖的存儲結構除了要存儲圖中各個頂點的本身信息外，同時還要存儲頂點與頂點之間的所有關係(邊的信息)，因此，圖的結構比較複雜，很難以數據元素在存儲區中的物理位置來表示元素之間的關係，但也正是由於其任意的特性，故物理表示方法很多。常用的圖的存儲結構有鄰接矩陣、鄰接表等。

## 鄰接矩陣表示法

對於一個具有n個結點的圖，可以使用n*n的矩陣(二維數組)來表示它們間的鄰接關係。矩陣 A(i,j) = 1 表示圖中存在一條邊 (Vi,Vj),而A(i,j)=0表示圖中不存在邊 (Vi,Vj)。
實際編程時，當圖為不帶權圖時，可以在二維數組中存放 bool 值。

* A(i,j) = true 表示存在邊 (Vi,Vj),
* A(i,j) = false 表示不存在邊 (Vi,Vj);


當圖帶權值時，則可以直接在二維數值中存放權值，A(i,j) = null 表示不存在邊 (Vi,Vj)。

下面看看我們使用鄰接矩陣實現的圖結構：

```rust
#[derive(Debug)]
struct Node {
    nodeid: usize,
    nodename: String,
}

#[derive(Debug,Clone)]
struct Edge {
    edge: bool,
}

#[derive(Debug)]
struct Graphadj {
    nodenums: usize,
    graphadj: Vec<Vec<Edge>>,
}

impl Node {
    fn new(nodeid: usize, nodename: String) -> Node {
        Node{
            nodeid: nodeid,
            nodename: nodename,
        }
    }
}
impl Edge {
    fn new() -> Edge {
        Edge{
            edge: false,
        }
    }
    fn have_edge() -> Edge {
        Edge{
            edge: true,
        }
    }
}

impl Graphadj {
    fn new(nums:usize) -> Graphadj {
        Graphadj {
            nodenums: nums,
            graphadj: vec![vec![Edge::new();nums]; nums],
        }
    }

    fn insert_edge(&mut self, v1: Node, v2:Node) {
        match v1.nodeid < self.nodenums && v2.nodeid<self.nodenums {
            true => {
                self.graphadj[v1.nodeid][v2.nodeid] = Edge::have_edge();
                //下面這句註釋去掉相當於把圖當成無向圖
                //self.graphadj[v2.nodeid][v1.nodeid] = Edge::have_edge();
            }
            false => {
                panic!("your nodeid is bigger than nodenums!");
            }
        }
    }
}

fn main() {
    let mut g = Graphadj::new(2);
    let v1 = Node::new(0, "v1".to_string());
    let v2 = Node::new(1, "v2".to_string());
    g.insert_edge(v1,v2);
    println!("{:?}", g);
}
```

## 鄰接表表示法

鄰接表是圖的一種最主要存儲結構，用來描述圖上的每一個點。

>**實現方式：**對圖的每個頂點建立一個容器（n個頂點建立n個容器），第i個容器中的結點包含頂點Vi的所有鄰接頂點。實際上我們常用的鄰接矩陣就是一種未離散化每個點的邊集的鄰接表。

* 在有向圖中，描述每個點向別的節點連的邊（點 a->點 b 這種情況）。
* 在無向圖中，描述每個點所有的邊(點 a->點 b這種情況)

與鄰接表相對應的存圖方式叫做邊集表，這種方法用一個容器存儲所有的邊。

## **練習：**
實現鏈接表表示法的圖結構。
