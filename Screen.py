from utils import *

class ScreenNode:
    def __init__(self):
        # 包名 + activity + 可点击组件的内部文本
        self.info = ""
        # self.sig = ""
        self.all_text = ""
        # # 当前screen的上一个screen
        # self.parent = None
        # 当前screen的下一个screen
        self.children = []
        # 记录着当前screen的所有可点击组件uid
        self.clickable_elements = None
        self.diff_clickable_elements = None
        self.merged_diff = -1
        self.pkg_name = ""
        self.class_name = ""
        self.activity_name = ""


        # call_map:{key:widget_uuid, value: next_screen_node}
        # call_map主要记录哪些组件能到达下一个Screen
        self.call_map = {}
        # 记录每个组件的uid的点击次数 {key:cur_clickable_ele_uid, val:cnt}
        self.ele_uid_cnt_map = {}
        # 记录组件是否有被点击过 {key:cur_clickable_ele_uid, val:true/false}
        self.ele_vis_map = {}
        # 记录当前screen已经被点击过的组件个数
        self.already_clicked_cnt = 0

    def get_diff_or_clickable_eles(self):
        if self.diff_clickable_elements is None:
            return self.clickable_elements
        else:
            return self.diff_clickable_elements

    def get_exactly_clickable_eles(self):
        return self.clickable_elements

    # 判断当前Screen是否点完了
    def is_screen_clickable_finished(self):
        if self.clickable_elements is None:
            raise Exception
        if self.diff_clickable_elements is None:
            if self.already_clicked_cnt == len(self.clickable_elements):
                return True
            else:
                return False
        else:
            if self.already_clicked_cnt == len(self.diff_clickable_elements):
                return True
            else:
                return False
    
    def add_child(self, child):
        # child.parent = self
        if child not in self.children:
            self.children.append(child)

    
    # def find_ancestor(self, target_screen_all_text):
    #     cur = self
    #     par = cur.parent
    #     while par is not None:
    #         if par.all_text == target_screen_all_text:
    #             return True
    #         cur = par
    #         par = cur.parent
    #     # print(cur.value)
    #     return False

    
    # 只检测level1的children是否全部完成
    def is_cur_callmap_finish(self, target_screen_all_text, screen_compare_strategy):
        if self is None:
            return True


        # for child_node in self.children:
        #     if screen_compare_strategy.compare_screen(child_node.all_text, target_screen_all_text)[0] == True:
        #     # if child_node.all_text == target_screen_all_text:
        #         if child_node.already_clicked_cnt == len(child_node.clickable_elements):
        #             return True
        #         else:
        #             return False
        # return True


        # 根据call_map来找,其实call_map和children差不多,区别就是children有回边,call_map没有
        #TODO
        for child_node in self.call_map.values():
            if screen_compare_strategy.compare_screen(child_node.all_text, target_screen_all_text)[0] == True:
            # if child_node.all_text == target_screen_all_text:
            #     if child_node.already_clicked_cnt == len(child_node.clickable_elements):
                if child_node.is_screen_clickable_finished():
                    return True
                else:
                    return False
        return True
            