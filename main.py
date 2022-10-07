from funcaptcha_solver import funcaptcha

# Replace public_key and site with your key/site
funcap = funcaptcha(
    public_key="",
    site="",
)

bad_captchas = 0


def solve_captcha():
    global bad_captchas
    while True:
        answer = funcap.solve()
        error = answer["error"]
        if error is None:
            answer["bad_captchas"] = bad_captchas
            return answer["token"]
        if "not_supported" in error:
            return "Site not supported / does not have audio challenges"
        if "too high" in error:
            return "Ratelimited"
        else:
            bad_captchas += 1


captcha_token = solve_captcha()
print(captcha_token)
