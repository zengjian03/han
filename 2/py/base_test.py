import json
import time
import unittest
import os
import sys

# 添加必要的路径以便导入模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.t4_daemon import _manager
from base.spider import BaseSpider
from cachetools import cached, TTLCache

# 每次测试完自动清理可能存在的类共享变量问题(0关闭 1启用)
AUTO_CLEAR = 0


# 计算斐波那契数列

def get_cache_key(n):
    return n


# 不加缓存的递归实现
def fibonacci_no_cache(n):
    if n < 2:
        return n
    return fibonacci_no_cache(n - 1) + fibonacci_no_cache(n - 2)


# 加缓存的递归实现
@cached(cache=TTLCache(maxsize=100, ttl=3600), key=get_cache_key)
def fibonacci_with_cache(n):
    if n < 2:
        return n
    return fibonacci_with_cache(n - 1) + fibonacci_with_cache(n - 2)


def to_json(item):
    if not item:
        return item
    if isinstance(item, dict) or isinstance(item, list):
        return json.dumps(item, ensure_ascii=False)
    return item


def to_object(item):
    if not item:
        return item
    if isinstance(item, dict) or isinstance(item, list):
        return item
    try:
        # 尝试解析JSON字符串
        return json.loads(item)
    except (json.JSONDecodeError, TypeError):
        # 如果不是有效的JSON字符串，返回原值
        return item


class TestDemoFunctions(unittest.TestCase):

    def test_get_cache_key(self):
        self.assertEqual(get_cache_key(5), 5)
        self.assertEqual(get_cache_key("test"), "test")

    def test_fibonacci_no_cache(self):
        self.assertEqual(fibonacci_no_cache(0), 0)
        self.assertEqual(fibonacci_no_cache(1), 1)
        self.assertEqual(fibonacci_no_cache(5), 5)
        self.assertEqual(fibonacci_no_cache(10), 55)

    def test_fibonacci_with_cache(self):
        # 清除缓存以确保测试准确性
        fibonacci_with_cache.cache_clear()

        self.assertEqual(fibonacci_with_cache(0), 0)
        self.assertEqual(fibonacci_with_cache(1), 1)
        self.assertEqual(fibonacci_with_cache(5), 5)
        self.assertEqual(fibonacci_with_cache(10), 55)

        # 测试缓存是否工作
        start_time = time.time()
        result1 = fibonacci_with_cache(10)
        first_call_time = time.time() - start_time

        start_time = time.time()
        result2 = fibonacci_with_cache(10)
        second_call_time = time.time() - start_time

        self.assertEqual(result1, result2)
        self.assertLessEqual(second_call_time, first_call_time)

    def test_to_json(self):
        # 测试字典转换
        test_dict = {"key": "value", "num": 123}
        result = to_json(test_dict)
        self.assertEqual(result, '{"key": "value", "num": 123}')

        # 测试列表转换
        test_list = [1, 2, 3]
        result = to_json(test_list)
        self.assertEqual(result, '[1, 2, 3]')

        # 测试字符串不变
        test_str = "already a string"
        result = to_json(test_str)
        self.assertEqual(result, test_str)

        # 测试None不变
        self.assertIsNone(to_json(None))

    def test_to_object(self):
        # 测试JSON字符串转换
        json_str = '{"key": "value", "num": 123}'
        result = to_object(json_str)
        self.assertEqual(result, {"key": "value", "num": 123})

        # 测试字典不变
        test_dict = {"key": "value"}
        result = to_object(test_dict)
        self.assertEqual(result, test_dict)

        # 测试列表不变
        test_list = [1, 2, 3]
        result = to_object(test_list)
        self.assertEqual(result, test_list)

        # 测试非JSON字符串返回原值
        test_str = "not a json string"
        result = to_object(test_str)
        self.assertEqual(result, test_str)

        # 测试None不变
        self.assertIsNone(to_object(None))

        # 测试无效JSON字符串返回原值
        invalid_json = "{invalid: json}"
        result = to_object(invalid_json)
        self.assertEqual(result, invalid_json)

    def test_encrypt_demo(self):
        input_str = '这是需要gzip加密的字符串'
        output_str = BaseSpider.gzip(input_str)
        self.assertIsInstance(output_str, str)

        decompressed_str = BaseSpider.ungzip(output_str)
        self.assertEqual(decompressed_str, input_str)

    def test_speed_demo(self):
        n = 25
        # 测试无缓存版本
        t1 = time.time()
        result1 = fibonacci_no_cache(n)
        t2 = time.time()
        cost_no_cache = round((t2 - t1) * 1000, 8)

        # 测试有缓存版本
        t3 = time.time()
        result2 = fibonacci_with_cache(n)
        t4 = time.time()
        cost_with_cache = round((t4 - t3) * 1000, 8)

        # 结果应该相同
        self.assertEqual(result1, result2)

        # 有缓存的版本应该更快
        self.assertLess(cost_with_cache, cost_no_cache * 10)

        print(f'无缓存耗时: {cost_no_cache:.6f}毫秒, 有缓存耗时: {cost_with_cache:.6f}毫秒')

    def _test_script_functionality(self, script_path, ext_dict):
        """测试脚本功能的通用方法"""
        if not os.path.exists(script_path):
            self.skipTest(f"需要{script_path}文件才能运行此测试")

        env = {
            'proxyUrl': '',
            'ext': ext_dict,
        }
        env_str = to_json(env)

        # 测试home调用
        home_result = _manager.call(script_path, 'home', env_str, [1])
        home_result_obj = to_object(home_result)
        self.assertIsInstance(home_result_obj, dict)

        # 测试homeVod调用
        homeVod_result = _manager.call(script_path, 'homeVod', env_str, [])
        homeVod_result_obj = to_object(homeVod_result)
        self.assertIsInstance(homeVod_result_obj, dict)

        # 如果有分类数据，继续测试其他功能
        if home_result_obj and 'class' in home_result_obj and home_result_obj['class']:
            type_name = home_result_obj['class'][0]['type_name']
            type_id = home_result_obj['class'][0]['type_id']

            # 测试category调用
            category_result = _manager.call(script_path, 'category', env_str, [type_id, 1, 1, {}])
            category_result_obj = to_object(category_result)
            self.assertIsInstance(category_result_obj, dict)

            # 如果有分类列表数据，继续测试详情功能
            if category_result_obj and 'list' in category_result_obj and category_result_obj['list']:
                vod_id = category_result_obj['list'][0]['vod_id']

                # 测试detail调用
                detail_result = _manager.call(script_path, 'detail', env_str, [[vod_id]])
                detail_result_obj = to_object(detail_result)
                self.assertIsInstance(detail_result_obj, dict)

                # 如果有详情数据，继续测试播放功能
                if detail_result_obj and 'list' in detail_result_obj and detail_result_obj['list']:
                    vod_play_url = detail_result_obj['list'][0].get('vod_play_url', '')
                    vod_play_from = detail_result_obj['list'][0].get('vod_play_from', '')

                    if vod_play_url and vod_play_from:
                        # 解析播放URL
                        play_parts = vod_play_url.split('#')[0].split('$')
                        if len(play_parts) > 1:
                            play = play_parts[1]

                            # 测试play调用
                            play_result = _manager.call(script_path, 'play', env_str, [vod_play_from, play, []])
                            play_result_obj = to_object(play_result)
                            self.assertIsInstance(play_result_obj, dict)

        # 测试search调用
        key = '测试'
        search_result = _manager.call(script_path, 'search', env_str, [key, 0, 1])
        search_result_obj = to_object(search_result)
        self.assertIsInstance(search_result_obj, dict)

        return True

    def test_apphs_script_shiguang(self):
        """测试AppHs.py脚本，使用shiguang配置"""
        script_path = './AppHs.py'
        ext_dict = {
            "host": "https://dy.jmzp.net.cn",
            "app_id": "shiguang",
            "deviceid": "",
            "versionCode": "10000",
            "UMENG_CHANNEL": "guan"
        }
        self._test_script_functionality(script_path, ext_dict)

    def test_apphs_script_xuebao(self):
        """测试AppHs.py脚本，使用xuebao配置"""
        script_path = './AppHs.py'
        ext_dict = {
            "host": "https://dy.jszdzs.com",
            "app_id": "xuebao",
            "deviceid": "",
            "versionCode": "21300",
            "UMENG_CHANNEL": "share"
        }
        self._test_script_functionality(script_path, ext_dict)

    def test_apphs_script_haigou(self):
        """测试AppHs.py脚本，使用haigou配置"""
        script_path = './AppHs.py'
        ext_dict = {
            "host": "https://dy.stxbed.com",
            "app_id": "haigou",
            "deviceid": "",
            "versionCode": "20100",
            "UMENG_CHANNEL": "zhuan"
        }
        self.functionality = self._test_script_functionality(script_path, ext_dict)

    def test_appyqk_script_1(self):
        """测试AppYqk.py脚本，使用一起看配置"""
        script_path = './AppYqk.py'
        ext_dict = {
            "host": "https://gapi0320.3njzmrx1.com/config.json,https://gapi0320.lq0okex8.com/config.json,https://gapi0320.zabqs8xp.com/config.json,https://yappconfig-20250628-1318635097.cos.ap-shanghai.myqcloud.com/config.json,https://yconfig-20250628-1360051343.cos.ap-guangzhou.myqcloud.com/config.json",
            "appId": "d6d520ea90904f1ba680ed6c9c9f9007", "appkey": "70af67d2b6cf47679b397ea4c1886877",
            "udid": "bfc18c00-c866-46cb-8d7b-121c39b942d4", "bundlerId": "com.flotimingo.ts", "source": "1001_default",
            "version": "1.3.10", "versionCode": 1104}
        self._test_script_functionality(script_path, ext_dict)

    def test_apphs_script_haigou2(self):
        from AppHs import Spider
        spider = Spider(t4_api='')
        ext_dict = {
            "host": "https://dy.stxbed.com",
            "app_id": "haigou",
            "deviceid": "",
            "versionCode": "20100",
            "UMENG_CHANNEL": "zhuan"
        }
        spider.setExtendInfo(to_json(ext_dict))
        spider.init('')
        home_result = spider.homeContent(1)
        print(home_result)
        self.assertIsInstance(home_result, dict)
        home_video_result = spider.homeVideoContent()
        print(home_video_result)
        self.assertIsInstance(home_video_result, dict)

    def test_qimao_novel_script(self):
        """测试七猫小说脚本"""
        script_path = './七猫小说[书].py'
        ext_dict = {}  # 根据需要添加七猫小说的配置
        self._test_script_functionality(script_path, ext_dict)

    def tearDown(self):
        """在每个测试方法后清理可能的状态"""
        if AUTO_CLEAR:
            # 清理管理器中的实例和正在初始化的对象
            with _manager._lock:
                _manager._instances.clear()
                _manager._inflight.clear()

            # 清理可能存在的模块引用
            for module_name in list(sys.modules.keys()):
                if module_name.startswith("t4_spider_"):
                    del sys.modules[module_name]


if __name__ == '__main__':
    unittest.main()
