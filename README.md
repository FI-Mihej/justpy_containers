# JustPy Components

Framework around an improved [JustPy](https://github.com/justpy-org/justpy) with an improved security, latency and concurrency. Based on [Cengal](https://github.com/FI-Mihej/Cengal) library and [https://github.com/YouCannotBurnMyShadow/justpy](https://github.com/YouCannotBurnMyShadow/justpy) fork (backward compatible with an original JustPy). Page construction process is similar to other my project: [flet_async](https://github.com/FI-Mihej/flet_async)

## ! Note !

I've encoutered a huge data-loss as a result of a Russia war against Ukrane. So currently I still manually restoring lost functionality of all my projects that have not gone completely.

So not all features are restored yet.

And not all features was completely ready even before the data loss: theme change without page reload has a bug and so currently it requires and makes an automatic page reload on a theme-change, for example.

## Features

* Page constructed with ierarchically placed Components (see example)
* Theme change from the page with an appropriate component. Themes are Tailwind-based and easy to create.
* Translation change from the page (without page reload) with an appropriate component. Translation changes for all opened pages in current session or for a current user
* Auto-translation using AWS Translate
* Preffered language detection. Initiall page content is sent to the browser in a best awailable language.
* Right-to-left languages support with an appropriate page direction change in runtime
* Client type detection for a page scale adjustments: desktop, smartphone, tab/pad.
* Users-sessions and user-less-sessions support
* GDPR-compliant. You may accept first request from the user without any cookies and only after user approve, redirect user to the same page but with required cookies turned on. And wise-versa.
* Key-value DB service (LMDB-based) for storring user settings and all you additionally need
* Improved security: original JustPy at least prior to version 2.0 has for example single html-tag counter for whole app instance (user can access and modify data in components on pages of other users). And other improvements.
* Improved latency for a big number of concurrent clients: original JustPy at least prior to version 2.0 can be totally unresponsive for other clients for about 200-400 ms on an each page rendering. And other fixes

## Example

Next example

* registers four themes: light, light_tranparent, dark and dark_transparent. Theme information provided by Node and other mechanisms.
* uses few manually created language translations plus over 60 machine-translated. Text chunks in `tt()` are translatable. Page translation changes without page reloading. Translation info provided by Node and other mechanisms.
* page rendering code is an async coroutine (Cengal coroutine) which interoperates with asyncio loops in the same thread

```python
class CncMadeApp(JpRunner):
    def return_web_page_body_classes(self) -> str:
        return 'flex flex-col min-h-screen'
    
    def return_path_to_log_dir(self) -> str:
        return path_relative_to_current_src('cnc_made/log.db')
    
    def return_path_to_sessions_dir(self) -> str:
        return path_relative_to_current_src('cnc_made/lmdb.db')
    
    async def return_text_dictionary(self) -> str:
        try:
            path_to_file = path_relative_to_current_src('cnc_made/text_dictionaly.json')
            with open(path_to_file, 'r', encoding='utf-8') as file:
                return file.read()
        except:
            return await super().return_text_dictionary()
    
    def return_default_theme_id(self) -> Theme:
        return 'dark'
    
    @page()
    def home_page(self, interface: Interface, request: Request, wp: jp.WebPage, root: Node, tokens: Tuple):
        ...
    
    @page()
    def individual_order(self, interface: Interface, request: Request, wp: jp.WebPage, root: Node, tokens: Tuple):
        ...
    
    @page()
    def shop(self, interface: Interface, request: Request, wp: jp.WebPage, root: Node, tokens: Tuple):
        ...

    @page()
    def not_found_404(self, interface: Interface, request: Request, wp: jp.WebPage, root: Node, tokens: Tuple):
        # This is Cengal coroutine: this is async code and can not hang asyncio loop (while working inside it)
        page_id, session_id, user_id = tokens

        project_name = TMe(tt('Ops! Page Not Found'))
        root.jp_set_title(project_name)
        with root()(ScreenWithHeaderAndFooter) as screen:
            with screen()(jp.Div, classes='w-full flex flex-col items-center') as div_center:
                div_center()(jp.Div, classes='h-16')
                div_center()(jp.H1, text=project_name)
                div_center()(jp.Div, classes='h-16')
                div_center()(jp.A, href='/', text=TMe(tt('Go to Homepage')), classes='text-base')
            
            with screen('footer')(FooterWithLangSelect) as footer:
                footer()(FooterContentSimple, TMe(tt('Made by MyCompany Inc.')))
    
    def return_routes(self) -> Tuple[Callable, Dict[str, Callable]]:
        return None, {
            '/': self.home_page,
            '/shop': self.shop,
            '/individual_order': self.individual_order
        }
    
    def init(self):
        self.register_theme('dark', dark_theme)
        self.register_theme('dark_transparent', dark_transparent_theme)
        self.register_theme('light', light_theme)
        self.register_theme('light_transparent', light_transparent_theme)
        self.set_main_page(self.not_found_404)

CncMadeApp()()
```

## License

Copyright © 2022 ButenkoMS. All rights reserved.

Licensed under the Apache License, Version 2.0.
