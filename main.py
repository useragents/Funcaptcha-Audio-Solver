from funcaptcha_solver import funcaptcha

#Replace public_key and site with your key/site
funcap = funcaptcha(
	public_key = "site_key_here", 
	site = "site_link_here"
)

answer = funcap.solve()
print(answer)
