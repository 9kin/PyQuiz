import requests
import json
from threading import Thread
import time
import urllib.parse


class HostAPI:
	def __init__(self, url, quiz):
		self.url = url
		quiz = str(quiz).replace('\'', '"')
		url = f"{url}/host?{urllib.parse.urlencode({'quiz': quiz})}"
		res = requests.get(url).json()
		self.error = False
		if res == {'detail': 'error'}:
			self.error = True
			return
		self.key = res['key']
		self.id = res['id']

	def hash_error(self):
		return self.error

	def get_info(self):
		if not self.hash_error():
			url = f"{self.url}/status?game_id={self.id}&key={self.key}"
			return requests.get(url).json()

	def play(self):
		if not self.hash_error():
			url = f"{self.url}/{self.id}/play?key={self.key}"
			s = requests.get(url).json()
			return s == [1]

	def next(self):
		if not self.hash_error():
			url = f"{self.url}/{self.id}/next?key={self.key}"
			s = requests.get(url).json()
			return s == ["next"]

	def get_raiting(self):
		if self.hash_error():
			return
		res = self.get_info()['peoples']
		ans = []
		for person in res:
			ans.append((res[person]["score"] + res[person]["last"]["add"], res[person]["name"]))
		return ans

	def get_peoples(self):
		if self.hash_error():
			return
		res = self.get_info()['peoples']
		ans = [res[key]["name"] for key in res]
		return ans

class PlayerAPI:
	def __init__(self, url, id_, name):
		res = requests.get(f"{url}/{id_}/connect?name={name}").json()
		self.error = None
		if res == {'detail': 'name'}:
			self.error = "name is too short/long or 🚹 already uses it"
			return
		elif res == {'detail': 'game'}:
			self.error = "🎮 does not exist or has started"
			return
		self.url, self.id, self.name = url, id_, name
		self.key = res['key']

	def hash_error(self):
		return self.error != None

	def ans(self, ans):
		if not self.hash_error():
			return requests.get(f"{self.url}/{self.id}/reply?key={self.key}&ans={ans}").json() == {'detail': 'error'}

	def validate(self):
		if not self.hash_error():
			return requests.get(f"{self.url}/{self.id}/validate?key={self.key}").json()


	def wait(self):
		if not self.hash_error():
			return requests.get(f"{self.url}/{self.id}/wait?key={self.key}")

	def question_info(self):
		if not self.hash_error():
			res = requests.get(f"{self.url}/{self.id}/question_info?key={self.key}").json()
			return [res["ans"], res["time"]]

	def game_info(self):
		if not self.hash_error():
			return requests.get(f"{self.url}/{self.id}/game_info?key={self.key}").json()[0]

# List[Tuple[int, str]]
quiz = {"0": {"time": 2, "score": 100  , "question": "2 + 2 = ?", "answers": ["5", "2", "4", "999"], "true": 2}}

def main():
	a = PlayerAPI('http://127.0.0.1:8000', '100001', 'a')
	b = PlayerAPI('http://127.0.0.1:8000', '100001', 'b')
	c = PlayerAPI('http://127.0.0.1:8000', '100001', 'c')
	d = PlayerAPI('http://127.0.0.1:8000', '100001', 'd')

	a.wait()

	a.ans(1)
	b.ans(2)
	c.ans(3)

if __name__ == '__main__':
	main()
