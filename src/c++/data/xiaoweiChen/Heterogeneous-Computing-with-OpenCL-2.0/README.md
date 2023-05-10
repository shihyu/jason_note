
Heterogeneous Computing with OpenCL 2.0
=========================
*Third Edition*
-------------------------
- 作者：David Kaeli, Perhaad Mistry, Dana Schaa, Dong Ping Zhang
- 译者：陈晓伟

## 本书概述

作为对《Heterogeneour Computing with OpenCL 2.0 (Thrid Edition)》英文版的中文翻译。

本书将介绍在复杂环境下的OpenCL和并行编程。这里的复杂环境包含多种设备架构，比如：多芯CPU，GPU，以及完全集成的加速处理单元(APU)。在本修订版中将包含OpenCL 2.0最新的改进：
- 共享虚拟内存(*Shared virtual memory*)可增强编程的灵活性，从而能大幅度减少在数据转换上所消耗的资源和精力 
- 动态并行(*Dynamic parallelism*)将减少处理器上的负载，并避免瓶颈出现
- 对图像的支持有很大改善，并且集成OpenGL

为了能在不同的平台上进行工作，OpenCL将有助你充分发挥出异构平台的能力。本书的作者们都是异构计算和OpenCL社区的佼佼者，本书涉及到的内容有：内存空间、优化技能、相关扩展、调试与分析。书中还会涉及多个实际的案例，来展示高性能的算法、异构系统如何分配工作，以及嵌入式领域特殊的语言。当然，也会让读者使用OpenCL来实现一些基本算法的并行版本：
- 使用最新OpenCL 2.0标准的特性，包括内存处理、动态并行和图像特性
- 对实际的程序进行测试和调试，从而对抽象的模型概念进行理解，并解释使用OpenCL进行并行编程的准则及策略
- 本书的案例包含：图像分析、Web插件、粒子模拟、视频编辑、性能优化，等等

## 本书作者

### David Kaeli

David Kaeli在罗格斯大学(Rutgers University)获得电气工程学士和博士学位，在雪城大学(Syracuse University)获得计算机工程硕士学位，并管理东北大学计算机体系研究室(NUCAR)。1993年Kaeli加入东北大学，他之前在IBM任职12年，任职的最后7年在T.J. Watson研究中心(位于纽约，约克敦海茨)度过。现在，在东北大学工程学院(本科)(位于美国东北部，马萨诸塞州，州府波士顿)任职副院长，为ECE(电子和计算机工程专业，Electrical and Computer Engineering)系的系主任。

Kaeli博士合著超过200个学术出版物，其研究领域跨度也非常大，从微体系结构到后端编译器和软件工程。他主导了很多GPU计算方面的研究项目，并且现在是IEEE技术委员会，计算机体系结构方面的主席。他也是IEEE院士，以及ACM(国际计算机学会，Association for Computing Machinery)成员。

### Perhaad Mistry

Perhaad Mistry作为AMD公司工具组开发成员，任职于在位于波士顿设计中心，主要研究异构结构下使用的调试和性能分析工具，现居波士顿。他目前主要研究的是“共享内存及离散式GPU平台”(将要到来的平台)上的调试工具的研究。自2007年CUDA0.8发布后，Perhaad就开始研究GPU的架构和并行计算。他很喜欢使用GPGPU来实现医学成像算法，以及设计外科模拟器的感知数据结构。Perhaad目前在为下一代GPU平台研究调试工具和性能分析工具。

David Kaeli博士曾在学校建议Perhaad加入NUCAR。虽然，已经离开东北大学已经7年(在东北大学电子和计算机工程专业取得博士学位)，但是Perhaad仍然是NUCAR的一员，并且在并行相关的性能分析项目上给出中肯的建议。其在孟买大学(印度3所历史最悠久、规模最大的综合性大学之一)获得电气工程学士学位，并在东北大学获得计算机工程硕士学位。

### Dana Schaa

Dana Schaa在加州州立理工大学(Cal Poly，位于神路易斯奥比斯波，旧金山和洛杉矶的中间位置)获得计算机工程学士学位，并在东北大学获得电子和计算机专业硕士和博士学位。他在AMD公司为GPU架构建模，并且对GPU的内存系统、微架构、性能分析和通用计算十分感兴趣，也在这些方面表现的相当专业。他开发了一些基于OpenCL的医学影像应用，从实时三维超声到异构CT(电子计算机断层扫描，Computed Tomography)图像重构。2010年，Dana与其女友Jenny完婚，现在他们和他们可爱的喵都住在圣何塞。

### 张东萍(Dong Ping Zhang)

东萍(音译)在英国帝国学院(Imperial College London)获得计算机博士学位。她博士期间的研究方向是“时域和空域上的大型多模态生物医学分析”。现任职与AMD公司，为“百亿亿次级计算研究组”工作。其研究方向和AMD公司“异构系统架构组”有着很密切的合作。

加入AMD公司之前，她在帝国学院计算机系做博士后研究。2006年，在先进计算方面获得理学硕士学位。2010年，在计算机科学方面获得博士学位。这两个学位均由Daniel Rueckert教授授予(Daniel Rueckert教授曾在医学图像分析领域获得“2010年度世界最佳导师”称号)。2009年，她还曾在鹿特丹Erasmus医学中心作为生物医学成像组成员，短暂的工作过一段时间。

## 本书相关

- github 翻译地址：https://github.com/xiaoweiChen/Heterogeneous-Computing-with-OpenCL-2.0
