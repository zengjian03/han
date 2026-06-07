import importlib
import sys
import traceback
import json
import os

method_dict = {
    'init': 'init',
    'home': 'homeContent',
    'homeVod': 'homeVideoContent',
    'category': 'categoryContent',
    'detail': 'detailContent',
    'search': 'searchContent',
    'play': 'playerContent',
    'proxy': 'localProxy',
    'action': 'action',
}


def import_module(module_url):
    return importlib.import_module(module_url)


def load_spider(script_path, env):
    """动态加载指定路径的 Python 脚本并实例化 Spider 类"""
    try:
        env = json.loads(env)
    except json.JSONDecodeError:
        # 保持原始字符串
        pass

    try:
        script_name = os.path.basename(script_path)[:-3]
        print('load_spider:', script_name)
        module = import_module(script_name)

        # 检查 Spider 类是否存在
        if not hasattr(module, 'Spider'):
            raise AttributeError(f"Script {script_path} does not contain a 'Spider' class")

        proxyUrl = env.get('proxyUrl') if isinstance(env, dict) else ''
        # 实例化 Spider
        spider = module.Spider(t4_api=proxyUrl)
        return spider

    except Exception as e:
        # 打印详细错误信息
        error_msg = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(error_msg)


def t4_spider_init(spider, ext=''):
    # 调用方法
    spider.setExtendInfo(ext)
    # 获取依赖项
    depends = spider.getDependence() or []
    modules = []
    module_names = []
    for lib in depends:
        try:
            module = import_module(lib).Spider(t4_api=ext)
            modules.append(module)
            module_names.append(lib)
        except Exception as e:
            print(f'装载依赖{lib}发生错误:{e}')

    if len(module_names) > 0:
        print(f'当前依赖列表:{module_names}')

    result = spider.init(modules)
    setattr(spider, '_init_ok_', True)
    return spider, result


def call_spider_method(spider, method_name, env, args):
    """调用 Spider 实例的指定方法"""
    invoke_method_name = method_dict.get(method_name) or method_name
    try:
        # 检查方法是否存在
        if not hasattr(spider, invoke_method_name):
            raise AttributeError(f"Spider has no method named '{invoke_method_name}'")

        method = getattr(spider, invoke_method_name)

        # 解析参数
        parsed_args = []
        for arg in args:
            try:
                # 尝试解析 JSON
                parsed_args.append(json.loads(arg))
            except json.JSONDecodeError:
                # 保持原始字符串
                parsed_args.append(arg)
        try:
            env = json.loads(env)
        except json.JSONDecodeError:
            # 保持原始字符串
            pass

        print(f'parsed_args:{parsed_args}')

        if method_name == 'init':
            extend = parsed_args[0] if parsed_args and isinstance(parsed_args, list) else ''
            spider, result = t4_spider_init(spider, extend)
            #             result = spider.init(modules)
            return result
        else:
            if not hasattr(spider, '_init_ok_'):
                #                 spider,_ = t4_spider_init(spider,*parsed_args) # 需要传extend参数，暂时没有好办法
                #                 extend = parsed_args[0] if parsed_args and isinstance(parsed_args,list)  else ''
                #                 extend = env.get('ext','')
                extend = env.get('ext') if isinstance(env, dict) else ''
                spider, _ = t4_spider_init(spider, extend)
                method = getattr(spider, invoke_method_name)
            result = method(*parsed_args)
        # 返回结果
        if result:
            try:
                return spider.json2str(result)
            except Exception as e:
                pass
        return result

    except Exception as e:
        # 打印详细错误信息
        error_msg = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(error_msg)


def main():
    if len(sys.argv) < 3:
        print("Usage: python bridge.py <script_path> <method_name> [args...]")
        return
    script_path = sys.argv[1]
    method_name = sys.argv[2]
    env = sys.argv[3]
    args = sys.argv[4:]
    print(f'script_path:{script_path},method_name:{method_name}')
    spider = load_spider(script_path, env)
    result = call_spider_method(spider, method_name, env, args)
    print(result)


if __name__ == '__main__':
    main()
