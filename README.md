# stttt2003pk_gslb_control

## Introduction

### isp_change_cmd

我们在维护互联网线上的GSLB广域网负载均衡调度的时候，总会因为配置过于负载导致运维人员各种僵硬
我的一个客户采用的就是根据中国各省各个运营商的地址库的调度
如：region jinan server: SH_OANet_OA
当我们的线路出现问题的时候我们需要将流量进行实时的调整，主要针对的问题如下：

* 运营商线路的端口出现问题，有的GSLB无法调度，这个取决于GSLB的建设架构以及涉及的一些设备的功能。我的客户使用的是GTM，但是除了对线路上进行连通性检测，对于业务的检测还存在遗漏，所以当线路出现问题，需要快速的在多条线路之间去切换地址库和对应解析的地址
* 有时候内部需要进行业务演练，也需要快速切换线路解析，让业务快速过渡到不同的运营商线路上

**借住F5的icontrol库，制作了isp_change_cmd这个cmd操作脚本，可以快速的在运营商线路之间进行业务的切换**

* 流程图如下
![](https://raw.github.com/stttt2003pk/stttt2003pk_gslb_control/master/screenshot/iControll_procedure_GTM-region.png)

### topology_count

* 针对GSLB的调度编排，我们需要对编排里面的文档记录进行相应的分值计算，计算出相应的结果顺序，配置相应的配置文件进行快速的应用GSLB调度变更，topology的脚本能够帮助我们根据设定的值解决计算的问题

[value]()是针对各个server节点设计的算法权值
[topology]()是根据我们需要对应的应用编排生成的计算结果
