# 二叉樹

## 二叉樹簡介
在計算機科學中，二叉樹是每個節點最多有兩個子樹的樹結構。通常子樹被稱作“左子樹”（left subtree）和“右子樹”（right subtree）。二叉樹常被用於實現二叉查找樹和二叉heap。

>二叉查找樹的子節點與父節點的鍵一般滿足一定的順序關係，習慣上，左節點的鍵少於父親節點的鍵，右節點的鍵大於父親節點的鍵。

>二叉heap是一種特殊的heap，二叉heap是完全二元樹（二叉樹）或者是近似完全二元樹（二叉樹）。二叉heap有兩種：最大heap和最小heap。最大heap：父結點的鍵總是大於或等於任何一個子節點的鍵；最小heap：父結點的鍵總是小於或等於任何一個子節點的鍵。

>二叉樹的每個結點至多隻有二棵子樹(不存在度大於2的結點)，二叉樹的子樹有左右之分，次序不能顛倒。二叉樹的第i層至多有2^{i-1}個結點；深度為k的二叉樹至多有2^k-1個結點；對任何一棵二叉樹T，如果其終端結點數為n_0，度為2的結點數為n_2，則n_0=n_2+1。

>一棵深度為k，且有2^k-1個節點稱之為滿二叉樹；深度為k，有n個節點的二叉樹，當且僅當其每一個節點都與深度為k的滿二叉樹中，序號為1至n的節點對應時，稱之為完全二叉樹。

## 二叉樹與樹的區別
二叉樹*不是*樹的一種特殊情形，儘管其與樹有許多相似之處，但樹和二叉樹有兩個主要差別：

1. 樹中結點的最大度數沒有限制，而二叉樹結點的最大度數為2。
2. 樹的結點無左、右之分，而二叉樹的結點有左、右之分。

## 定義二叉樹的結構
二叉樹的每個節點由鍵key、值value與左右子樹left/right組成，這裡我們把節點聲明為一個泛型結構。

```rust
type TreeNode<K,V> = Option<Box<Node<K,V>>>;
#[derive(Debug)]
struct Node<K,V: std::fmt::Display> {
   left: TreeNode<K,V>,
   right: TreeNode<K,V>,
   key: K,
   value: V,
}
```

## 實現二叉樹的初始化與二叉查找樹的插入
由於二叉查找樹要求鍵可排序，我們要求K實現PartialOrd

```rust
trait BinaryTree<K,V> {
	fn pre_order(&self);
	fn in_order(&self);
	fn pos_order(&self);
}
trait BinarySearchTree<K:PartialOrd,V>:BinaryTree<K,V> {
	fn insert(&mut self, key:K,value: V);
}
impl<K,V:std::fmt::Display> Node<K,V> {
    fn new(key: K,value: V) -> Self {
        Node{
            left: None,
            right: None,
            value: value,
			key: key,
        }
    }
}
impl<K:PartialOrd,V:std::fmt::Display> BinarySearchTree<K,V> for Node<K,V>{
    fn insert(&mut self, key:K,value:V) {
        if self.key < key {
            if let Some(ref mut right) = self.right {
                right.insert(key,value);
            } else {
                self.right = Some(Box::new(Node::new(key,value)));
            }
        } else {
            if let Some(ref mut left) = self.left {
                left.insert(key,value);
            } else {
                self.left = Some(Box::new(Node::new(key,value)));
            }
        }
    }
}
```

## 二叉樹的遍歷

- 先序遍歷：首先訪問根，再先序遍歷左（右）子樹，最後先序遍歷右（左）子樹。
- 中序遍歷：首先中序遍歷左（右）子樹，再訪問根，最後中序遍歷右（左）子樹。
- 後序遍歷：首先後序遍歷左（右）子樹，再後序遍歷右（左）子樹，最後訪問根。

下面是代碼實現：

```rust
impl<K,V:std::fmt::Display> BinaryTree<K,V> for Node<K,V> {
    fn pre_order(&self) {
        println!("{}", self.value);

        if let Some(ref left) = self.left {
            left.pre_order();
        }
        if let Some(ref right) = self.right {
            right.pre_order();
        }
    }

    fn in_order(&self) {
        if let Some(ref left) = self.left {
            left.in_order();
        }
        println!("{}", self.value);
        if let Some(ref right) = self.right {
            right.in_order();
        }
    }
    fn pos_order(&self) {
        if let Some(ref left) = self.left {
            left.pos_order();
        }
        if let Some(ref right) = self.right {
            right.pos_order();
        }
        println!("{}", self.value);
    }
}
```

## 測試代碼

```rust
type BST<K,V> = Node<K,V>;

fn test_insert() {
    let mut root = BST::<i32,i32>::new(3,4);
    root.insert(2,3);
    root.insert(4,6);
    root.insert(5,5);
    root.insert(6,6);
    root.insert(1,8);
    if let Some(ref left) = root.left {
        assert_eq!(left.value, 3);
    }

    if let Some(ref right) = root.right {
        assert_eq!(right.value, 6);
        if let Some(ref right) = right.right {
            assert_eq!(right.value, 5);
        }
    }
    println!("Pre Order traversal");
    root.pre_order();
    println!("In Order traversal");
    root.in_order();
    println!("Pos Order traversal");
    root.pos_order();
}

fn main() {
    test_insert();
}
```

## 練習
基於以上代碼，修改成二叉heap的形式。
