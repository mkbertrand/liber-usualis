import os

# Accepts a file path (relative to /web/locales/{locale}/) and a list of locales in order of preference and returns the first locale that has the file. Basically needed for places where there's an English-only resource requested by a German user.
def bestlocalized(file, locales):
	for l in locales:
		if os.path.exists(f'web/locales/{l}{file}'):
			return f'web/locales/{l}{file}'
