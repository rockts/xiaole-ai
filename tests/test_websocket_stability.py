"""
WebSocket连接稳定性测试

测试场景：
1. 断线重连
2. 多客户端同时连接
3. 长连接保活
4. 消息并发
"""

import asyncio
import websockets
import json
from datetime import datetime


class WebSocketClient:
    """WebSocket客户端"""
    
    def __init__(self, client_id: str, url: str = "ws://localhost:8000/ws"):
        self.client_id = client_id
        self.url = url
        self.websocket = None
        self.connected = False
        self.messages_received = 0
        self.reconnect_count = 0
        
    async def connect(self):
        """建立连接"""
        try:
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            print(f"[{self.client_id}] ✅ 连接成功")
        except Exception as e:
            print(f"[{self.client_id}] ❌ 连接失败: {e}")
            self.connected = False
            
    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print(f"[{self.client_id}] 🔌 断开连接")
            
    async def listen(self, duration: int = 10):
        """监听消息"""
        print(f"[{self.client_id}] 👂 开始监听 {duration}秒...")
        start_time = datetime.now()
        
        try:
            while (datetime.now() - start_time).seconds < duration:
                if not self.connected:
                    break
                    
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=1.0
                    )
                    data = json.loads(message)
                    self.messages_received += 1
                    print(f"[{self.client_id}] 📨 收到消息 #{self.messages_received}: {data.get('type', 'unknown')}")
                    
                except asyncio.TimeoutError:
                    continue
                except websockets.exceptions.ConnectionClosed:
                    print(f"[{self.client_id}] ⚠️  连接关闭")
                    self.connected = False
                    break
                    
        except Exception as e:
            print(f"[{self.client_id}] ❌ 监听出错: {e}")
            
        print(f"[{self.client_id}] 📊 共收到 {self.messages_received} 条消息")
        
    async def auto_reconnect(self, duration: int = 30, reconnect_delay: int = 5):
        """自动重连测试"""
        print(f"\n[{self.client_id}] 🔄 自动重连测试（{duration}秒）")
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < duration:
            if not self.connected:
                await asyncio.sleep(reconnect_delay)
                print(f"[{self.client_id}] 🔄 尝试重连...")
                await self.connect()
                self.reconnect_count += 1
                
            await asyncio.sleep(1)
            
        print(f"[{self.client_id}] 📊 重连次数: {self.reconnect_count}")


async def test_basic_connection():
    """测试1: 基础连接"""
    print("\n" + "="*60)
    print("测试1: 基础连接")
    print("="*60)
    
    client = WebSocketClient("Client-1")
    await client.connect()
    
    if client.connected:
        await client.listen(duration=5)
        await client.disconnect()
        print("✅ 基础连接测试通过")
    else:
        print("❌ 基础连接测试失败")


async def test_reconnection():
    """测试2: 断线重连"""
    print("\n" + "="*60)
    print("测试2: 断线重连")
    print("="*60)
    
    client = WebSocketClient("Client-Reconnect")
    
    # 第一次连接
    await client.connect()
    await asyncio.sleep(2)
    
    # 主动断开
    await client.disconnect()
    await asyncio.sleep(2)
    
    # 尝试重连
    await client.connect()
    
    if client.connected:
        print("✅ 断线重连测试通过")
        await client.disconnect()
    else:
        print("❌ 断线重连测试失败")


async def test_multiple_clients():
    """测试3: 多客户端同时连接"""
    print("\n" + "="*60)
    print("测试3: 多客户端同时连接")
    print("="*60)
    
    clients = [
        WebSocketClient(f"Client-{i}")
        for i in range(1, 6)  # 创建5个客户端
    ]
    
    # 同时建立连接
    await asyncio.gather(*[client.connect() for client in clients])
    
    connected_count = sum(1 for c in clients if c.connected)
    print(f"\n📊 成功连接: {connected_count}/5")
    
    # 同时监听5秒
    await asyncio.gather(*[client.listen(duration=5) for client in clients])
    
    # 断开所有连接
    await asyncio.gather(*[client.disconnect() for client in clients])
    
    if connected_count == 5:
        print("✅ 多客户端测试通过")
    else:
        print(f"⚠️  多客户端测试部分通过 ({connected_count}/5)")


async def test_long_connection():
    """测试4: 长连接保活"""
    print("\n" + "="*60)
    print("测试4: 长连接保活（30秒）")
    print("="*60)
    
    client = WebSocketClient("Client-Long")
    await client.connect()
    
    if client.connected:
        await client.listen(duration=30)
        
        if client.connected:
            print("✅ 长连接保活测试通过")
        else:
            print("❌ 长连接中途断开")
            
        await client.disconnect()
    else:
        print("❌ 长连接测试失败（连接失败）")


async def test_message_storm():
    """测试5: 消息风暴（压力测试）"""
    print("\n" + "="*60)
    print("测试5: 消息风暴（多客户端并发接收）")
    print("="*60)
    
    print("\n💡 提示: 请在另一个终端运行以下命令触发多个提醒：")
    print("   python tests/test_websocket_push.py")
    print("\n等待10秒接收消息...")
    
    clients = [
        WebSocketClient(f"Storm-{i}")
        for i in range(1, 4)  # 3个客户端
    ]
    
    # 同时建立连接
    await asyncio.gather(*[client.connect() for client in clients])
    
    # 同时监听10秒
    await asyncio.gather(*[client.listen(duration=10) for client in clients])
    
    # 统计
    total_messages = sum(c.messages_received for c in clients)
    print(f"\n📊 总共收到 {total_messages} 条消息")
    
    # 断开所有连接
    await asyncio.gather(*[client.disconnect() for client in clients])
    
    if total_messages > 0:
        print("✅ 消息接收测试通过")
    else:
        print("⚠️  未收到消息（可能没有触发提醒）")


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 WebSocket 稳定性测试套件")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 测试1: 基础连接
        await test_basic_connection()
        await asyncio.sleep(2)
        
        # 测试2: 断线重连
        await test_reconnection()
        await asyncio.sleep(2)
        
        # 测试3: 多客户端
        await test_multiple_clients()
        await asyncio.sleep(2)
        
        # 测试4: 长连接（可选，比较耗时）
        # await test_long_connection()
        # await asyncio.sleep(2)
        
        # 测试5: 消息风暴
        await test_message_storm()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_all_tests())
