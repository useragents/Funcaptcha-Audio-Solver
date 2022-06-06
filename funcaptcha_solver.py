import requests, random, string, time, json
import speech_recognition as sr

class funcaptcha:

    def __init__(self, public_key, site):
        self.session = requests.Session()
        self.user_agent = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        self.url = "https://api.funcaptcha.com"
        self.public_key = public_key
        self.site = site
        self.start_time = time.time()
        self.retries = 1
        self.bad_captchas = 0
        self.headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "User-Agent": self.user_agent
        }

    def get_session_token(self):
        headers = {
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": self.site,
            "User-Agent": self.user_agent
        }
        rnd = "0." + ("").join(random.choices(string.digits, k = 17))
        data = {
            "bda": "",
            "public_key": self.public_key,
            "rnd": rnd,
            "site": self.site,
            "userbrowser": self.user_agent
        }
        r = self.session.post(
            self.url + "/fc/gt2/public_key/{}".format(self.public_key),
            headers = headers,
            data = data
        )
        captcha_token = r.json()["token"]
        session_token = captcha_token.split("|")[0]
        return session_token, captcha_token

    def get_game_token(self, session_token):
        data = {
            "lang": "",
            "sid": "eu-west-1",
            "analytics_tier": "40",
            "render_type": "canvas",
            "token": session_token,
            "data[status]": "init"
        }
        r = self.session.post(
            self.url + "/fc/gfct/",
            headers = self.headers,
            data = data
        )
        game_token = r.json()["challengeID"]
        return game_token
    
    def load_game(self, session_token, game_token):
        data = {
            "sid": "eu-west-1",
            "session_token": session_token,
            "render_type": "canvas",
            "game_type": "3",
            "game_token": game_token,
            "category": "loaded",
            "analytics_tier": "40",
            "action": "game loaded"
        }
        r = self.session.post(
            self.url + "/fc/a/",
            headers = self.headers,
            data = data
        )
    
    def switch_to_audio(self, session_token, game_token):
        data = {
            "sid": "eu-west-1",
            "session_token": session_token,
            "render_type": "canvas",
            "label": "swapped to audio captcha",
            "game_type": "3",
            "game_token": game_token,
            "category": "audio captcha",
            "analytics_tier": "40",
            "action": "user clicked audio"
        }
        r = self.session.post(
            self.url + "/fc/a/",
            headers = self.headers,
            data = data
        )
    
    def get_audio_captcha(self, session_token):
        data = {
            "session_token": session_token,
            "analytics_tier": "40",
            "r": "eu-west-1",
            "game": "0",
            "language": "en"
        }
        r = self.session.post(
            self.url + "/fc/get_audio/?session_token={}&analytics_tier=40&r=eu-west-1&game=0&language=en".format(session_token),
            headers = self.headers,
            data = data
        )
        if "DENIED ACCESS" in r.text:
            return False
        with open("audio.wav", "wb") as f:
            f.write(r.content)
        return True
    
    def most_frequent(self, list):
        try:
            return max(set(list), key = list.count)
        except ValueError:
            return None
    
    def solve_captcha(self):
        try:
            temp_reformed = []
            r = sr.Recognizer()
            with sr.WavFile("audio.wav") as source:
                r.adjust_for_ambient_noise(source)
                audio = r.record(source, duration = 7)
            response = r.recognize(audio, show_all = True)
            
            for text in response:
                reformed_text = self.replace_resp(text["text"])
                if len(reformed_text) == 7:
                    if reformed_text.isdigit():
                        temp_reformed.append(reformed_text)
            if len(reformed_text) != 0:
                response = self.most_frequent(temp_reformed)
                return response
            self.bad_captchas += 1
            self.solve()
        except LookupError:
            self.bad_captchas += 1
            self.solve()
     
    
    def replace_resp(self, resp: str): #Improves accuracy for speech recognition
        resp = resp.lower() 
        replacements = {
            "one": "1",
            "to": "2",
            "two": "2",
            "tree": "3",
            "three": "3",
            "four": "4",
            "for": "4",
            "or": "4",
            "zero": "0",
            "do": "5",
            "right": "5",
            "hero": "4",
            "five": "5",
            "six": "6",
            "nine": "9",
            "white": "1",
            "whine": "1",
            "dial": "69",
            "wine": "1",
            "guys": "9",
            "sides": "9",
            "store": "44",
            "door": "04",
            "side": "9",
            "buy": "55",
            "rightly": "53",
            "rightfully": "53",
            "lee": "53",
            "now": "9",
            "eight": "8",
            "soon": "2",
            "wireless": "8",
            "find": "5",
            "rise": "1",
            "italy": "34",
            "ice": "0",
            "lights": "9",
            "light": "9",
            "sites": "9",
            "pwell": "9",
            "well": "9",
            "size": "9",
            "by": "1",
            "knights": "9",
            "knight": "9",
            "nights": "9",
            "night": "9",
            "-": "",
            " ": "",
            "r": "9",
            "l": "2",
            "a": "4"
        }
        for key in replacements:
            if key in resp:
                resp = resp.replace(key, replacements[key])
        return resp

    def main(self):
        session_token, captcha_token = self.get_session_token()
        game_token = self.get_game_token(session_token)
        self.load_game(session_token, game_token)
        self.switch_to_audio(session_token, game_token)
        result = self.get_audio_captcha(session_token)
        if result == False:
            return session_token, "not_supported", None
        response = self.solve_captcha()
        if response == None:
            self.bad_captchas += 1
            return session_token, None, captcha_token
        if len(response) != 7 or not response.isdigit():
            self.bad_captchas += 1
            self.main()
        return session_token, response, captcha_token
    
    def solve(self):
        session_token, response, captcha_token = self.main()
        if response == None:
            answer = {"token": None, "error": "Bad captcha"}
            return answer
        if response == "not_supported":
            answer = {"token": None, "error": "site_not_supported"}
            return answer
        data = {
            "session_token": session_token,
            "analytics_tier": "40",
            "response": response,
            "language": "en",
            "r": "eu-west-1",
            "audio_type": "2",
            "bio": ""
        }
        r = self.session.post(
            self.url + "/fc/audio/",
            headers = self.headers,
            data = data
        )
        if "Incorrect, try again" in r.text:
            self.retries += 1
            answer = {"token": None, "error": "Bad captcha"}
            return answer
        elif "response" in r.text:
            if r.json()["response"] == "correct":
                solve_time = str(time.time() - self.start_time).split(".")[0]
                answer = {   
                    "token": captcha_token, 
                    "solve_time": solve_time + "s",
                    "error": None
                }
                return answer
            elif r.json()["response"] == "incorrect":
                answer = {"token": None, "error": r.json()["error_reply"]}
                return answer
