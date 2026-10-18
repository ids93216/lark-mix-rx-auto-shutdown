import argparse
import time

import hid


VID = 0x3547
REPORT_SIZE = 64

CMD_HEARTBEAT = 0x10
CMD_SHUTDOWN_TIME = 0x36
CMD_GET_SHUTDOWN_TIME = 0x28

TARGET_RX = 0x40


def build_packet(cmd, payload=b"", target=TARGET_RX):
	if len(payload) > 56:
		raise ValueError("Payload too long")

	packet = bytearray(REPORT_SIZE)
	packet[0] = 0x55
	packet[1] = 0xAA
	packet[2] = 0xDD
	packet[3] = cmd
	packet[4] = target
	packet[5] = (len(payload) >> 8) & 0xFF
	packet[6] = len(payload) & 0xFF
	packet[7:7 + len(payload)] = payload

	checksum = 0
	for value in packet[1:7 + len(payload)]:
		checksum ^= value

	packet[7 + len(payload)] = checksum

	return bytes(packet)


def dump(data):
	return " ".join(f"{x:02X}" for x in data)


def list_devices():
	devices = hid.enumerate(VID, 0)

	if not devices:
		print(f"找不到 VID=0x{VID:04X} 的 HID 裝置")
		return []

	for i, dev in enumerate(devices):
		print(f"[{i}]")
		print(f"  path         = {dev['path']!r}")
		print(f"  product      = {dev.get('product_string')}")
		print(f"  manufacturer = {dev.get('manufacturer_string')}")
		print(f"  serial       = {dev.get('serial_number')}")
		print(f"  PID          = 0x{dev['product_id']:04X}")
		print(f"  interface    = {dev.get('interface_number')}")
		print(f"  usage_page   = 0x{(dev.get('usage_page') or 0):04X}")
		print(f"  usage        = 0x{(dev.get('usage') or 0):04X}")
		print()

	return devices


def open_device(index):
	devices = hid.enumerate(VID, 0)

	if index < 0 or index >= len(devices):
		raise RuntimeError(f"裝置 index {index} 不存在")

	dev = hid.device()
	dev.open_path(devices[index]["path"])
	dev.set_nonblocking(False)

	return dev


def send_command(dev, cmd, payload=b"", timeout_ms=1000):
	packet = build_packet(cmd, payload)

	print(f"TX: {dump(packet[:10 + len(payload)])}")

	written = dev.write(packet)
	print(f"write = {written}")

	responses = []

	while True:
		data = dev.read(REPORT_SIZE, timeout_ms)

		if not data:
			break

		data = bytes(data)
		responses.append(data)
		print(f"RX: {dump(data)}")

		# 第一包之後縮短 timeout，看看還有沒有後續回包
		timeout_ms = 100

	return responses


def heartbeat(dev):
	print("\n=== Heartbeat ===")
	return send_command(dev, CMD_HEARTBEAT)


def get_shutdown_time(dev):
	print("\n=== Get Shutdown Time ===")
	responses = send_command(dev, CMD_GET_SHUTDOWN_TIME)

	if not responses:
		print("沒有回包，可能 6301RX 不支援 ProtocolV2 的 0x28")
		return None

	for data in responses:
		print(f"RAW: {dump(data)}")

	return responses


def set_shutdown_time(dev, never=True):
	value = 1 if never else 0

	print(f"\n=== Shutdown Time: {'Never' if never else '15min'} ===")
	packet = build_packet(CMD_SHUTDOWN_TIME, bytes([value]))

	print(f"TX: {dump(packet[:10])}")

	written = dev.write(packet)
	print(f"write = {written}")

	data = dev.read(REPORT_SIZE, 500)

	if data:
		print(f"RX: {dump(bytes(data))}")
	else:
		print("RX: 無回包（setter 可能本來就不回 ACK）")


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--device", type=int, default=None, help="hid.enumerate() 顯示的裝置編號")
	parser.add_argument("--never", action="store_true", help="設定 RX 為永不自動關機")
	parser.add_argument("--auto", dest="auto", action="store_true", help="恢復自動關機")
	parser.add_argument("--get-shutdown", action="store_true", help="讀取目前自動關機設定")
	args = parser.parse_args()

	devices = list_devices()

	if not devices:
		return

	if args.device is None:
		print("先確認上面的 HID interface，再用 --device N 指定。")
		print("例如：python lark_mix_rx.py --device 2")
		return

	dev = open_device(args.device)

	try:
		heartbeat(dev)

		if args.never:
			set_shutdown_time(dev, True)

		if args.auto:
			set_shutdown_time(dev, False)

		if args.get_shutdown:
			get_shutdown_time(dev)

	finally:
		dev.close()


if __name__ == "__main__":
	main()