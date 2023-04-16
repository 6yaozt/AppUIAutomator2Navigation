# cur_activity
# for....所有能点击的组件:
#   click()
# 否则当前没东西可点了，back ，不写成dfs
from utils import *
from Screen import *
from ScreenCompareStrategy import *
import time
import signal
 
 
# 自定义超时异常
class TimeoutError(Exception):
    def __init__(self, msg):
        super(TimeoutError, self).__init__()
        self.msg = msg
 
 
def time_out(interval, callback):
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutError("run func timeout")
 
        def wrapper(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handler)
                signal.alarm(interval)       # interval秒后向进程发送SIGALRM信号
                result = func(*args, **kwargs)
                signal.alarm(0)              # 函数在规定时间执行完后关闭alarm闹钟
                return result
            except TimeoutError as e:
                callback(e)
        return wrapper
    return decorator
 
 
def timeout_callback(e):
    print("超时回调函数")
 


@time_out(3, timeout_callback)
def testTimeOut():
    while(True):
        print(100)
        time.sleep(1)


def dfs_screen(last_screen_sig, last_clickable_ele, last_activity):
    # 获取当前screen

    cur_screen_pkg_name, cur_activity, cur_screen_all_text, cur_screen_info = get_screen_info(d)
    cur_screen_sig = get_signature(cur_screen_info)


    if cur_screen_pkg_name != target_pkg_name:
        d.press("back")
        time.sleep(5)
        return

    #EditText点击之后或者其他情况会有输入框，此时无法点击其他组件
    #因此需要back消除输入框，然后return
    if last_clickable_ele is not None:
        # 用更加 general的方法来规避输入法输入框
        if("EditText" in last_clickable_ele.get("class")):
            # print("文本框回退")
            d.press("back")
            return
        elif (d(packageName = "com.google.android.inputmethod.latin").exists()):
            # print("文本框回退")
            d.press("back")
            cur_screen_pkg_name, cur_activity, cur_screen_all_text, cur_screen_info = get_screen_info(d)
            cur_screen_sig = get_signature(cur_screen_info)
    
    # screen没有变化说明该组件不会造成页面跳转
    if cur_screen_sig == last_screen_sig:
        return
    
    stat_activity_set.add(cur_activity) #统计结果用
    stat_screen_set.add(cur_screen_sig) #统计结果用

    # 建Screen跳转图
    cur_screen_node = None
    if screen_map.get(cur_screen_sig, False) == False:
        # 初始化cur_screen_node信息
        cur_screen_node = ScreenNode()
        cur_screen_node.info = cur_screen_info
        cur_screen_node.sig = cur_screen_sig
        cur_screen_node.all_text = cur_screen_all_text
        cur_screen_node.pkg_name = cur_screen_pkg_name
        cur_screen_node.activity_name = cur_activity
        clickable_eles = get_clickable_elements(d, umap, cur_activity)
        cur_screen_node.clickable_elements = clickable_eles
        # 将cur_screen加入到全局记录的screen_map
        screen_map[cur_screen_sig] = cur_screen_node
        # 将cur_screen加入到last_screen的子节点
        last_screen_node = screen_map.get(last_screen_sig)
        last_screen_node.add_child(cur_screen_node)
    else:
        cur_screen_node = screen_map.get(cur_screen_sig)
    print("*"*100)
    print(f"Screen--{cur_screen_node.all_text[0:20]}--{len(cur_screen_node.clickable_elements)}")
    print("*"*100)
    

    #如果触发了新的界面，这个时候要判断是否存在回边，存在环就不加call_map
    #表示虽然该组件能触发新界面，但是会产生回边，因此不能将screen加入call_map
    if last_screen_sig != "root":
        last_screen_node = screen_map.get(last_screen_sig)
        if last_screen_node.find_ancestor(cur_screen_sig):
            #产生了回边
            pass
        else:
            last_clickale_ele_uuid = get_uuid(last_clickable_ele, d, umap, last_activity)
            last_screen_node.call_map[last_clickale_ele_uuid] = cur_screen_sig
    
    # 遍历cur_screen的所有可点击组件
    cur_screen_node_clickable_eles = cur_screen_node.clickable_elements
    for cur_clickable_ele in cur_screen_node_clickable_eles:
        #--------------------------------------
        #判断当前组件是否需要访问
        #1.如果没访问过，即vis_map[uuid]=False，就直接访问
        #2.如果访问过了，即vis_map[uuid]=True,还得判断该组件是否是
        #当前callmap的，如果是还需要递归判断该组件对应的call_map里面的节点(screen)
        #的所有组件是否访问完毕

        #判断当前界面是否真的为当前界面？
        temp_screen_pkg, temp_activity, temp_screen_all_text, temp_screen_info = get_screen_info(d)
        temp_screen_sig = get_signature(temp_screen_info)
        if (cur_screen_pkg_name != temp_screen_pkg) or (cur_activity != temp_activity):
            print("循环过程中界面不一样导致回退-----------------------")
            return
        if not screen_compare_strategy.compare_screen(cur_screen_all_text, temp_screen_all_text):
            print("循环过程中界面不一样导致回退-----------------------")
            return

        uuid = get_uuid(cur_clickable_ele, d, umap, cur_activity)

        global total_eles_cnt
        if ele_vis_map.get(uuid, False) == False:
            # 拿到该组件的坐标x, y
            loc_x, loc_y = get_location(cur_clickable_ele)
            ele_vis_map[uuid] = True
            #点击该组件
            cur_screen_node.already_clicked_cnt = get_uuid_cnt(uuid)
            print(f"点击组件: {uuid}-----------------------")
            total_eles_cnt +=1 #统计的组件点击次数+1

            d.click(loc_x, loc_y)
            time.sleep(5)
            dfs_screen(cur_screen_sig, cur_clickable_ele, cur_activity)

        else:
            if cur_screen_node.call_map.get(uuid, None) is not None:
                target_screen_sig = cur_screen_node.call_map.get(uuid)
                if not cur_screen_node.is_all_children_finish(target_screen_sig):
                    # click_map指示存在部分没完成
                    loc_x, loc_y = get_location(cur_clickable_ele)
                    # 点击该组件
                    cur_screen_node.already_clicked_cnt = get_uuid_cnt(uuid)
                    print(f"点击组件: {uuid}-----------------------")
                    total_eles_cnt +=1 #统计的组件点击次数+1
                    d.click(loc_x, loc_y) 
                    time.sleep(5)
                    dfs_screen(cur_screen_sig, cur_clickable_ele, cur_activity)
    # for循环遍历结束back返回上一层界面

    print("正常回退")
    d.press("back")
    time.sleep(5)

if __name__ == "__main__":


    # try:
    #     testTimeOut()
    # except Exception as e:
    #     print(1)
    # 存储着整个app所有screen(ScrennNode) {key:screen_sig, val:screen_node}
    screen_map = {}
    # umap: {key:uid, value:cnt}
    umap = {}
    # 全局记录每个组件的uuid {key:uuid, val:clickable_ele}
    ele_uuid_map = {}
    # 全局记录组件是否有被点击过 {key:uuid, val:true/false}
    ele_vis_map = {}

    # 统计结果用
    total_eles_cnt = 0
    stat_screen_set = set()
    # total_screen_cnt = 0
    stat_activity_set = set()
    # total_activity_cnt = 0


    # 启动app开始执行
    d = Device()
    screen_compare_strategy = ScreenCompareStrategy(LCSComparator())
    # curr_pkg_name = "com.example.myapplication"
    target_pkg_name = "com.alibaba.android.rimet"
    # target_pkg_name = "com.ss.android.lark"
    # target_pkg_name = "com.cloudy.component"
    # target_pkg_name = "com.jingyao.easybike"
    d.app_start(target_pkg_name)
    time.sleep(5)
    root_sig = "root"
    root = ScreenNode()
    root.sig = root_sig
    screen_map["root"] = root

    # try:
    dfs_screen(root_sig, None, None)
    # except Exception as e:
    #     print(e)

    print("@"*100)
    print("@"*100)
    print(f"总共点击的activity个数 {len(stat_activity_set)}")
    print(f"总共点击的Screen个数: {len(stat_screen_set)}")
    print(f"总共点击的组件个数: {total_eles_cnt}")
