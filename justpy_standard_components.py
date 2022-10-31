__all__ = [
 'WebPageForApp','WindowTitleTextForApp','Screen','ScreenWithHeaderAndFooter','ScreenWithStickyHeaderAndFooter','AnAppScreenWithStickyHeaderAndFooter','Pannels','LanguageSelector','ThemeSelector','ThemeSelectorForApp','Main','Header','HeaderForApp','Footer','FooterCendered','FooterWithLangSelect','FooterWithLangSelectLayered','FooterWithLangSelectForApp','FooterWithLangSelectLayeredForApp','FooterContentSimple','InitialRequestView','ComponentTreeReloader','LoginForm','LoginFormForApp','RegisterForm','Progressbar','AvailableComputingPower','Tooltip','UserAgentIndicator','DetectMetaSize','MetaSizeIndicator','DetectDeviceScreenSizes','DeviceScreenSizesIndicator']
from pprint import pprint
import uuid
from pandas.core.dtypes.common import classes
from low_latency_justpy import justpy as jp, init_scheduler
from justpy_components import *
from justpy_coro_helpers import *
from typing import NoReturn, Union, Optional, Dict, Set, List, Tuple, Type, Callable, Sequence, cast
from cengal.parallel_execution.coroutines import *
from cengal.parallel_execution.coroutines.coro_standard_services.async_event_bus import *
from cengal.parallel_execution.coroutines.coro_standard_services.log import *
from cengal.parallel_execution.coroutines.coro_standard_services.asyncio_loop import *
from cengal.parallel_execution.coroutines.coro_standard_services.kill_coro import *
from cengal.parallel_execution.coroutines.coro_tools.await_coro import create_task
from cengal.text_processing.text_translator import *
from cengal.statistics.normal_distribution import *
from time import perf_counter
from math import ceil, sqrt
import sys
from cengal.performance_test_lib import test_run_time
from enum import Enum
from cengal.introspection.inspect import is_async, is_callable

class WebPageForApp(jp.WebPage):
    pass


class WindowTitleTextForApp(jp.P):
    pass


class Screen(CoroComponent):

    def construct(self):
        self.html = self.container = self.stheme('screen', (jp.Div), classes='h-screen w-screen inset-0 flex')


class ScreenWithHeaderAndFooter(CoroComponent):

    def init(self):
        self.header = None
        self.main = None
        self.footer = None

    def construct(self):
        self.html = self.stheme('screen', (jp.Div), classes='h-screen w-screen inset-0 flex flex-col min-h-screen')
        self.containers['header'] = self.theme((jp.Div), a=(self.html))
        self.containers['main'] = self.theme((jp.Div), a=(self.html), classes='flex-grow')
        self.containers['footer'] = self.theme((jp.Div), a=(self.html))
        self.container = self.containers['main']


class ScreenWithStickyHeaderAndFooter(CoroComponent):
    __doc__ = '\n    https://dev.to/cryptic022/sticky-header-and-footer-with-tailwind-2oik\n    '

    def init(self, sticky_header: bool=True, sticky_footer: bool=True):
        self.sticky_header = sticky_header
        self.sticky_footer = sticky_footer
        self.header = None
        self.main = None
        self.footer = None

    def construct(self):
        self.html = self.stheme('screen', (jp.Div), classes='h-screen w-screen inset-0 flex flex-col min-h-screen')
        if self.sticky_header:
            self.containers['header'] = self.theme((jp.Header), a=(self.html))
        else:
            self.containers['header'] = self.theme((jp.Div), a=(self.html))
        if self.sticky_header and self.sticky_footer:
            self.containers['main'] = self.theme((jp.Main), a=(self.html), classes='flex-1 overflow-y-auto')
        else:
            self.containers['main'] = self.theme((jp.Div), a=(self.html), classes='flex-grow')
        if self.sticky_header:
            self.containers['footer'] = self.theme((jp.Footer), a=(self.html))
        else:
            self.containers['footer'] = self.theme((jp.Div), a=(self.html))
        self.container = self.containers['main']


class AnAppScreenWithStickyHeaderAndFooter(CoroComponent):
    __doc__ = '\n    https://dev.to/cryptic022/sticky-header-and-footer-with-tailwind-2oik\n    '

    def init(self, app_name: str, sticky_footer: bool=True):
        self.app_name = app_name
        self.sticky_footer = sticky_footer
        self.header = None
        self.main = None
        self.footer = None

    def construct(self, root: Node):
        root.jp_set_title(self.app_name)
        with root().subc('screen', ScreenWithStickyHeaderAndFooter, True, True) as screen:
            with screen('header')(HeaderForApp) as app_header:
                with app_header()((jp.Div), classes='flex-auto flex flex-row items-center') as div_title:
                    div_title()((jp.Div), classes='flex-shrink flex w-16')
                    div_title()((jp.Div), classes='flex-shrink flex w-3')
                    div_title()((jp.Div), classes='flex-auto flex')
                    div_title()(WindowTitleTextForApp, text=(self.app_name), classes='whitespace-nowrap flex-shrink')
                    div_title()((jp.Div), classes='flex-auto flex')
        self.containers = screen.item.containers


class Pannels(CoroComponent):

    def construct(self):
        self.html = self.theme((jp.Div), classes='h-full flex')
        self.containers['pan_l'] = self.stheme('pan_l_classes', (jp.Div), a=(self.html), classes='h-auto overflow-y-auto')
        pan_r_holder = self.theme((jp.Div), a=(self.html), classes='flex-1 flex overflow-hidden')
        self.container = self.containers['pan_r'] = self.stheme('pan_r_classes', (jp.Div), a=pan_r_holder, classes='flex-1 overflow-y-auto')


class LanguageSelector(CoroComponent):

    def init(self):
        self.on_language_change_coro_id = None
        self.need_to_stop_coros = False

    def construct(self):
        self.html = self.theme((jp.Div), classes='w-auto h-auto')
        translator_data = self.translate.text_translator.text_translator.decoded_data
        manually_translated_to = set(translator_data['manually_translated_to'])
        auto_translated_to = set(translator_data['auto_translated_to'])
        languages = sorted(list(manually_translated_to)) + sorted(list(auto_translated_to))
        language_names = translator_data['laguages_names']
        lang = self.translate.text_translator.end_lang
        self.selector = self.stheme('selector', (jp.Select), a=(self.html), value=lang, change=(self.on_selector_change))
        bold_classes_cache = None
        normal_classes_cache = None
        for language in languages:
            language_name = language_names[language]
            if language in manually_translated_to:
                if bold_classes_cache is None:
                    item = self.stheme('selector_language', (jp.Option), value=language, text=language_name, classes='font-bold')
                    bold_classes_cache = item._classes
                else:
                    item = jp.Option(value=language, text=language_name, classes=bold_classes_cache)
                self.selector.add(item)
            else:
                if normal_classes_cache is None:
                    item = self.stheme('selector_language', (jp.Option), value=language, text=language_name)
                    normal_classes_cache = item._classes
                else:
                    item = jp.Option(value=language, text=language_name, classes=normal_classes_cache)
                self.selector.add(item)

        app = cast(JpRunner, self.jp_web_page.application_instance)

        def on_language_change(interface: Interface, self):
            while not self.need_to_stop_coros:
                lang, end_lang = interface(AsyncEventBus, AsyncEventBusRequest().wait(self.translate.text_translator.translation_language_changed_event))
                self.selector.value = end_lang
                self.jp_ensure_update_web_page()

                async def make_page_rtl(jp_web_page):
                    await jp_web_page.run_javascript("\n                    document.body.setAttribute('dir', 'rtl');\n                    ")

                async def make_page_ltr(jp_web_page):
                    await jp_web_page.run_javascript("\n                    document.body.setAttribute('dir', 'ltr');\n                    ")

                translator_data = self.translate.text_translator.text_translator.decoded_data
                if end_lang in translator_data['rtl_languages']:
                    acoro = make_page_rtl
                else:
                    acoro = make_page_ltr
                create_task(self.asyncio_loop, acoro, self.jp_web_page)

        async def on_page_ready_handler(*args, **kwargs):
            self.on_language_change_coro_id = await self.await_task_fast(PutCoro, on_language_change, self)

        app.add_on_page_event(self.jp_web_page.page_id, 'page_ready', on_page_ready_handler)

    @coro_event_handler()
    def on_selector_change(interface: Interface, self, item, msg):
        start_time = perf_counter()
        self.translate.text_translator.lang = msg['value']
        self.translate.reapply()
        end_time = perf_counter()
        delta_time = end_time - start_time
        return False

    def delete_impl(self, i):
        self.need_to_stop_coros = True
        if self.on_language_change_coro_id is not None:
            i(KillCoro, self.on_language_change_coro_id)


class ThemeSelector(CoroComponent):

    def init(self, session_id: str, user_id):
        self.session_id = session_id
        self.user_id = user_id

    def construct(self, node: Node):
        with node().subc('html', (jp.Div), classes='w-auto h-auto') as html:
            self.html = html.item
            themes = sorted(self.jp_web_page.application_instance._themes.keys())
            app = cast(JpRunner, self.jp_web_page.application_instance)
            if self.session_id is None:
                current_theme_id = app.return_default_theme_id()
                with html().subc('dilabled_selector', (jp.Select), disabled=True, value=current_theme_id, change=(self.on_selector_change)) as selector:
                    self.selector = selector.item
            else:
                current_settings = app.current_settings(self.session_id, self.user_id)
                current_theme_id = current_settings['_base']['theme.theme_id']
                with html().subc('selector', (jp.Select), value=current_theme_id, change=(self.on_selector_change)) as selector:
                    self.selector = selector.item
            for theme in themes:
                option = selector().subc('selector_language', (jp.Option), value=theme, text=(TMe(tt(f"{theme.title()} theme"))))

            if self.session_id is None:
                html()(Tooltip, (Tooltip.Positioning.top), text=(TMe('{}!', tt('Allow cookies to change theme'))))

    @coro_event_handler()
    def on_selector_change(i: Interface, self, item, msg):
        app = cast(JpRunner, self.jp_web_page.application_instance)
        current_settings = app.current_settings(self.session_id, self.user_id)
        theme_id = msg['value']
        current_settings['_base']['theme.theme_id'] = theme_id
        current_settings['_objects']['theme_args_manager'] = ThemeArgsManager(app.get_theme(theme_id))
        io_loop = i(AsyncioLoop, AsyncioLoopRequest().get())
        page_ids_to_reload = app.session_pages.get(self.session_id)
        for page_id_to_reload in page_ids_to_reload:
            create_task(io_loop, jp.WebPage.instances[page_id_to_reload].reload)

        return False


class ThemeSelectorForApp(ThemeSelector):

    def construct(self, node: Node):
        with node()((jp.Div), classes='w-auto h-auto') as html:
            self.html = html.item
            themes = sorted([theme for theme in self.jp_web_page.application_instance._themes.keys() if theme.startswith('app_')])
            app = cast(JpRunner, self.jp_web_page.application_instance)
            if self.session_id is None:
                current_theme_id = app.return_default_theme_id()
                with html().subc('dilabled_selector', (jp.Select), disabled=True, value='disabled') as selector:
                    self.selector = selector.item
                    selector().subc('selector_language', (jp.Option), value='disabled', text=(TMe('{} ({})', tt(f"{current_theme_id.title()} theme"), tt('Allow cookies to change theme'))))
            else:
                current_settings = app.current_settings(self.session_id, self.user_id)
                current_theme_id = current_settings['_base']['theme.theme_id']
                with html().subc('selector', (jp.Select), value=current_theme_id, change=(self.on_selector_change)) as selector:
                    self.selector = selector.item
            for theme in themes:
                theme_name = theme[len('app_'):]
                selector().subc('selector_language', (jp.Option), value=theme, text=(TMe(tt(f"{theme_name.title()} theme"))))


class Main(CoroComponent):

    def construct(self):
        self.html = self.container = self.stheme('html_container', (jp.Div), classes='flex-grow flex')


class Header(CoroComponent):

    def construct(self, node: Node):
        with node().subc('html', (jp.Div), classes='flex flex-row') as html:
            self.html = html.item
            with html()((jp.Div), classes='flex-none pr-3') as left:
                left().subc('lang_select', LanguageSelector)
            self.container = html()((jp.Div), classes='flex-grow flex').item


class HeaderForApp(CoroComponent):

    def construct(self, node: Node):
        with node().subc('html', (jp.Div), classes='flex-auto pywebview-drag-region flex flex-row pl-0 pr-0') as html:
            self.html = html.item
            self.container = html()((jp.Div), classes='flex-auto flex').item
            with html()((jp.Div), classes='flex-shrink flex flex-row') as window_buttons:
                self.window_buttons_div = window_buttons.item
                self.window_minimize_button = window_buttons()((jp.Button), text='–', classes='-- rounded-none w-auto pl-3 pr-3 pt-0 pb-0 text-gray-500 hover:text-gray-100 hover:bg-gray-800 transition duration-250 ease-in-out font-normal transform hover:translate-y-0 h-8 z-50', click=(self.on_window_minimize_button)).item
                self.window_maximize_button = window_buttons()((jp.Button), text='#', classes='-- rounded-none w-auto pl-3 pr-3 pt-0 pb-0 text-gray-500 hover:text-gray-100 hover:bg-gray-800 transition duration-250 ease-in-out font-normal transform hover:translate-y-0 h-8 z-50', click=(self.on_window_toggle_fullscreen_button)).item
                self.window_close_button = window_buttons()((jp.Button), text='X', classes='-- rounded-none w-auto pl-3 pr-3 pt-0 pb-0 text-gray-500 hover:text-gray-100 hover:bg-red-600 transition duration-250 ease-in-out font-normal transform hover:translate-y-0 h-8 z-50', click=(self.on_window_close_button)).item

    @staticmethod
    async def on_window_close_button(self, msg):
        await msg.page.run_javascript('\n        pywebview.api.close_window();\n        ')

    @staticmethod
    async def on_window_minimize_button(self, msg):
        await msg.page.run_javascript('\n        pywebview.api.minimize_window();\n        ')

    @staticmethod
    async def on_window_maximize_button(self, msg):
        await msg.page.run_javascript('\n        pywebview.api.maximize_window();\n        ')

    @staticmethod
    async def on_window_restore_button(self, msg):
        await msg.page.run_javascript('\n        pywebview.api.restore_window();\n        ')

    @staticmethod
    async def on_window_toggle_fullscreen_button(self, msg):
        await msg.page.run_javascript('\n        pywebview.api.toggle_fullscreen();\n        ')


class Footer(CoroComponent):

    def construct(self):
        self.html = self.stheme('html', (jp.Div), classes='flex flex-row')
        self.container = self.theme((jp.Div), a=(self.html), classes='flex-grow flex')


class FooterCendered(CoroComponent):

    def construct(self):
        self.html = self.stheme('html', (jp.Div), classes='flex flex-row')
        l_placeholder = self.theme((jp.Div), a=(self.html), classes='flex-grow')
        self.container = self.theme((jp.Div), a=(self.html), classes='flex-grow-0 flex')
        r_placeholder = self.theme((jp.Div), a=(self.html), classes='flex-grow')


class FooterWithLangSelect(CoroComponent):

    def construct(self, node: Node):
        with node().subc('html', (jp.Div), classes='flex flex-row') as html:
            self.html = html.item
            with html()((jp.Div), classes='flex-none pr-3') as left:
                left().subc('lang_select', LanguageSelector)
            self.container = html()((jp.Div), classes='flex-grow flex').item


class FooterWithLangSelectLayered(CoroComponent):

    def construct(self, node: Node):
        with node().subc('html', (jp.Div), classes='flex-auto flex flex-col') as html:
            self.html = html.item
            with html()((jp.Div), classes='flex-auto flex flex-row pr-3') as top_row:
                self.containers['top'] = top_row.item
                top_row().subc('lang_select', LanguageSelector)
            self.container = html()((jp.Div), classes='flex-auto flex flex-col').item


class FooterWithLangSelectForApp(CoroComponent):

    def construct(self, node: Node):
        with node().subc('html', (jp.Div), classes='flex flex-row') as html:
            self.html = html.item
            with html()((jp.Div), classes='flex-none pr-3') as left:
                left().subc('lang_select', LanguageSelector)
            self.container = html()((jp.Div), classes='flex-grow flex').item


class FooterWithLangSelectLayeredForApp(CoroComponent):

    def construct(self, node: Node):
        with node().subc('html', (jp.Div), classes='flex-auto flex flex-col') as html:
            self.html = html.item
            with html()((jp.Div), classes='flex-auto flex flex-row pr-3') as top_row:
                self.containers['top'] = top_row.item
                top_row().subc('lang_select', LanguageSelector)
            self.container = html()((jp.Div), classes='flex-auto flex flex-col').item


class FooterContentSimple(CoroComponent):

    def init(self, text: Optional[TranslateMe]=None):
        self.text = text

    def construct(self):
        self.html = self.theme((jp.Div), classes='flex-grow flex')
        l_placeholder = self.theme((jp.Div), a=(self.html), classes='flex-grow')
        container = self.theme((jp.Div), a=(self.html), classes='flex-grow-0 flex items-center')
        r_placeholder = self.theme((jp.Div), a=(self.html), classes='flex-grow')
        footer_text = self.stheme('html', (jp.P), a=container)
        if self.text:
            self.jp_set_text(footer_text, self.text)


class InitialRequestView(CoroComponent):

    def init(self, request: Request):
        self.request = request

    def construct(self):
        self.html = self.stheme('html', (jp.Div), classes='-- h-auto overflow-hidden')
        head = self.theme((jp.Div), a=(self.html), classes='select-none text-base mt-2 ml-2 mr-2 p-1 bg-gray-900 text-yellow-500 font-bold rounded-t border-b')
        self.jp_set_text(head, '{}', tt("Client's Initial Request Info"))
        body = self.theme((jp.Div), a=(self.html), classes='h-auto overflow-y-auto mb-2 ml-2 mr-2 p-1 bg-gray-900 text-gray-400 rounded-b text-base')
        body_app_head = self.theme((jp.P), classes='select-none font-medium font-sans text-xs font-bold subpixel-antialiased not-italic text-yellow-500', a=body)
        self.jp_set_text(body_app_head, '{}:', tt('Application'))
        body_app_content = self.theme((jp.P), a=body, text=(self.request.app), classes='border-b mb-2 pb-1')
        body_url_head = self.theme((jp.P), classes='select-none font-medium font-sans text-xs font-bold subpixel-antialiased not-italic text-yellow-500', a=body)
        self.jp_set_text(body_url_head, '{}:', tt('URL'))
        body_url_content = self.theme((jp.P), a=body, text=(self.request.url), classes='border-b mb-2 pb-1')
        body_base_url_head = self.theme((jp.P), classes='select-none font-medium font-sans text-xs font-bold subpixel-antialiased not-italic text-yellow-500', a=body)
        self.jp_set_text(body_base_url_head, '{}:', tt('Base URL'))
        body_base_url_content = self.theme((jp.P), a=body, text=(self.request.base_url), classes='border-b mb-2 pb-1')
        body_headers_head = self.theme((jp.P), classes='select-none font-medium font-sans text-xs font-bold subpixel-antialiased not-italic text-yellow-500', a=body)
        self.jp_set_text(body_headers_head, '{}:', tt('Headers'))
        body_headers_content = self.theme((jp.P), a=body, text=(self.request.headers), classes='border-b mb-2 pb-1')
        body_query_params_head = self.theme((jp.P), classes='select-none font-medium font-sans text-xs font-bold subpixel-antialiased not-italic text-yellow-500', a=body)
        self.jp_set_text(body_query_params_head, '{}:', tt('Query Parameters'))
        body_query_params_content = self.theme((jp.P), a=body, text=(self.request.query_params), classes='border-b mb-2 pb-1')
        body_path_params_head = self.theme((jp.P), classes='select-none font-medium font-sans text-xs font-bold subpixel-antialiased not-italic text-yellow-500', a=body)
        self.jp_set_text(body_path_params_head, '{}:', tt('Path Parameters'))
        body_path_params_content = self.theme((jp.P), a=body, text=(self.request.path_params), classes='border-b mb-2 pb-1')
        body_cookies_head = self.theme((jp.P), classes='select-none font-medium font-sans text-xs font-bold subpixel-antialiased not-italic text-yellow-500', a=body)
        self.jp_set_text(body_cookies_head, '{}:', tt('Cookies'))
        body_cookies_content = self.theme((jp.P), a=body, text=(self.request.cookies), classes='border-b mb-2 pb-1')
        body_client_head = self.theme((jp.P), classes='select-none font-medium font-sans text-xs font-bold subpixel-antialiased not-italic text-yellow-500', a=body)
        self.jp_set_text(body_client_head, '{}:', tt('Client'))
        body_client_content = self.theme((jp.P), a=body, text=(self.request.client), classes='mb-2 pb-1')


class ComponentTreeReloader(CoroComponent):

    def init(self, root_component: 'Component', renderer: Callable, after_delete: Optional[Callable]=None, before_render: Optional[Callable]=None):
        self.root_component = root_component
        self.renderer = renderer
        self.after_delete = after_delete
        self.before_render = before_render

    def construct(self):
        self.html = self.theme((jp.Div), classes='-- w-auto h-auto')
        self.button = self.theme((jp.Button), a=(self.html))
        self.jp_set_text(self.button, '{}', tt('Reload Components Tree'))
        self.button.on('click', self.on_button_click_coro)

    @event_handler()
    async def on_button_click_coro(self, item, msg):
        await self.await_task_fast(Log, 'Button clicked')

        def remove_tree(interface: Interface, self, item, msg):
            self.root_component.delete()
            if self.after_delete is not None:
                self.after_delete()

        await self.await_coro_fast(remove_tree, self, item, msg)
        await self.await_task_fast(Log, 'Tree removed')
        await msg.page.update()
        wait_time = 5.0
        update_time_interval = 1.0
        while wait_time > 0.0:
            self.jp_set_text(self.button, '{}... {} {}', tt('Reloading Components Tree'), wait_time, tt('seconds until reload'))
            await msg.page.update()
            await self.await_task_fast(Sleep, update_time_interval)
            wait_time -= update_time_interval

        self.jp_set_text(self.button, '{}...', tt('Components tree rendering'))
        await self.await_task_fast(Log, 'Waiting completed')

        def render_tree(interface: Interface, self, item, msg):
            if self.before_render is not None:
                self.before_render()
            self.root_component = self.renderer()

        await self.await_coro_fast(render_tree, self, item, msg)
        self.jp_set_text(self.button, '{}', tt('Reload Components Tree'))
        await self.await_task_fast(Log, 'Tree rendered')


class LoginForm(CoroComponent):

    def construct(self):
        self.html = self.theme((jp.Div), classes='inset-0 absolute select-none')
        self.background = self.stheme('background', Screen, (self.html), classes={'screen': 'absolute select-none'})
        self.frontend = self.theme((jp.Div), a=(self.html), classes='h-screen w-screen inset-0 absolute select-none')
        row_holder = self.theme((jp.Div), a=(self.frontend), classes='flex flex-row')
        l_placeholder = self.theme((jp.Div), a=row_holder, classes='flex-grow')
        row = self.theme((jp.Div), a=row_holder, classes='flex-grow-0')
        r_placeholder = self.theme((jp.Div), a=row_holder, classes='flex-grow')
        col_holder = self.theme((jp.Div), a=row, classes='flex flex-col justify-between')
        t_placeholder = self.theme((jp.Div), a=col_holder, classes='flex-grow sm:h-16 md:h-24 lg:h-32 xl:h-48')
        col = self.theme((jp.Div), a=col_holder, classes='flex-grow-0')
        b_placeholder = self.theme((jp.Div), a=col_holder, classes='flex-grow')
        login_form = self.stheme('form', (jp.Div), a=col_holder, classes='self-center flex flex-col justify-center')
        drow1 = self.theme((jp.Div), a=login_form, classes='flex flex-row')
        dl1 = self.theme((jp.Div), a=drow1, classes='flex-grow-0')
        self.lang_selector = self.stheme(None, LanguageSelector, dl1)
        c_placeholder = self.theme((jp.Div), a=drow1, classes='flex-grow')
        dr1 = self.theme((jp.Div), a=drow1, classes='flex-grow-0')
        close_form_button = self.stheme('form_close_button', (jp.Button), text='X', a=dr1, classes='-- w-auto -p-1 pl-2 pr-2 pt-0 pb-0 transition duration-250 ease-in-out font-bold transform hover:scale-125 hover:translate-y-0 hover:font-normal')
        close_form_button.on('click', self.on_close_form)
        head = self.stheme('form_head', (jp.Div), a=login_form, classes='select-none text-base mt-2 ml-2 mr-2 p-1 font-bold rounded-t border-b')
        self.jp_set_text(head, '{}', tt('Login Form'))
        form1 = jp.Form(a=login_form, classes='m-5 p-3 font-bold w-64')
        user_label = self.stheme('user_name_label', (jp.Label), classes='-- block uppercase tracking-wide mb-2', a=form1)
        self.jp_set_text(user_label, '{}', tt('User Name'))
        in1 = self.stheme('user_name_input', (jp.Input), a=form1, classes='-- form-input')
        self.jp_set_placeholder(in1, '{}', tt('User Name'))
        user_label.for_component = in1
        password_label = self.stheme('user_password_label', (jp.Label), classes='-- block uppercase tracking-wide mb-2 mt-2', a=form1)
        pass_div = jp.Div(classes='block uppercase tracking-wide text-gray-400 text-xs font-bold mb-2', a=password_label)
        self.jp_set_text(pass_div, '{}', tt('Password'))
        in2 = self.stheme('user_password_input', (jp.Input), a=password_label, classes='-- form-input text-base', type='password')
        self.jp_set_placeholder(in2, '{}', tt('Password'))
        check_label = self.stheme('send_stuff_label', (jp.Label), classes='-- block', a=form1)
        self.stheme('send_stuff_checkbox', (jp.Input), type='checkbox', a=check_label, classes='-- form-checkbox')
        send_stuff_span = jp.Span(a=check_label, classes='ml-2 text-gray-400 font-normal')
        self.jp_set_text(send_stuff_span, '{}', tt('Send me stuff'))
        submit_button = self.stheme('form_submit_button', (jp.Input), type='submit', a=form1, classes='self-center', forced_theme=(jp.Button))
        self.jp_set_value(submit_button, '{}', tt('Submit Form'))
        form1.on('submit', self.on_submit_form)

    @coro_event_handler()
    def on_close_form(i: Interface, self, item, msg):
        print('on_close_form:')
        pprint(str(msg))
        self.remove()
        self.delete()

    @coro_event_handler()
    def on_submit_form(i: Interface, self, item, msg):
        print('on_submit_form:')
        pprint(str(msg))
        self.remove()
        self.delete()

    def delete_impl(self, i: Interface):
        print('delete_impl...')
        self.html.delete()
        self.background.delete()
        self.lang_selector.delete()
        print('delete_impl.')


class LoginFormForApp(LoginForm):

    def construct(self):
        self.html = self.theme((jp.Div), classes='inset-0 absolute select-none')
        self.background = self.stheme('background', Screen, (self.html), classes={'screen': 'absolute select-none'})
        self.frontend = self.stheme('frontend', AnAppScreenWithStickyHeaderAndFooter, (self.html), app_name='Login', sticky_footer=False)
        row_holder = self.theme((jp.Div), a=(self.frontend.container), classes='flex flex-row')
        l_placeholder = self.theme((jp.Div), a=row_holder, classes='flex-grow')
        row = self.theme((jp.Div), a=row_holder, classes='flex-grow-0')
        r_placeholder = self.theme((jp.Div), a=row_holder, classes='flex-grow')
        col_holder = self.theme((jp.Div), a=row, classes='flex flex-col justify-between')
        t_placeholder = self.theme((jp.Div), a=col_holder, classes='flex-grow sm:h-16 md:h-24 lg:h-32 xl:h-48')
        col = self.theme((jp.Div), a=col_holder, classes='flex-grow-0')
        b_placeholder = self.theme((jp.Div), a=col_holder, classes='flex-grow')
        login_form = self.stheme('form', (jp.Div), a=col_holder, classes='self-center flex flex-col justify-center')
        drow1 = self.theme((jp.Div), a=login_form, classes='flex flex-row')
        dl1 = self.theme((jp.Div), a=drow1, classes='flex-grow-0')
        self.lang_selector = self.stheme(None, LanguageSelector, dl1)
        c_placeholder = self.theme((jp.Div), a=drow1, classes='flex-grow')
        dr1 = self.theme((jp.Div), a=drow1, classes='flex-grow-0')
        close_form_button = self.stheme('form_close_button', (jp.Button), text='X', a=dr1, classes='-- w-auto -p-1 pl-2 pr-2 pt-0 pb-0 transition duration-250 ease-in-out font-bold transform hover:scale-125 hover:translate-y-0 hover:font-normal')
        close_form_button.on('click', self.on_close_form)
        head = self.stheme('form_head', (jp.Div), a=login_form, classes='select-none text-base mt-2 ml-2 mr-2 p-1 font-bold rounded-t border-b')
        self.jp_set_text(head, '{}', tt('Login Form'))
        form1 = jp.Form(a=login_form, classes='m-5 p-3 font-bold w-64')
        user_label = self.stheme('user_name_label', (jp.Label), classes='-- block uppercase tracking-wide mb-2', a=form1)
        self.jp_set_text(user_label, '{}', tt('User Name'))
        in1 = self.stheme('user_name_input', (jp.Input), a=form1, classes='-- form-input')
        self.jp_set_placeholder(in1, '{}', tt('User Name'))
        user_label.for_component = in1
        password_label = self.stheme('user_password_label', (jp.Label), classes='-- block uppercase tracking-wide mb-2 mt-2', a=form1)
        pass_div = jp.Div(classes='block uppercase tracking-wide text-gray-400 text-xs font-bold mb-2', a=password_label)
        self.jp_set_text(pass_div, '{}', tt('Password'))
        in2 = self.stheme('user_password_input', (jp.Input), a=password_label, classes='-- form-input text-base', type='password')
        self.jp_set_placeholder(in2, '{}', tt('Password'))
        check_label = self.stheme('send_stuff_label', (jp.Label), classes='-- block', a=form1)
        self.stheme('send_stuff_checkbox', (jp.Input), type='checkbox', a=check_label, classes='-- form-checkbox')
        send_stuff_span = jp.Span(a=check_label, classes='ml-2 text-gray-400 font-normal')
        self.jp_set_text(send_stuff_span, '{}', tt('Send me stuff'))
        submit_button = self.stheme('form_submit_button', (jp.Input), type='submit', a=form1, classes='self-center', forced_theme=(jp.Button))
        self.jp_set_value(submit_button, '{}', tt('Submit Form'))
        form1.on('submit', self.on_submit_form)


class RegisterForm(CoroComponent):

    def gen_background(self):
        return self.stheme('background', Screen, (self.html), classes={'screen': 'absolute select-none'})

    def construct(self):
        self.html = self.theme((jp.Div), classes='inset-0 absolute select-none')
        self.background = self.gen_background()
        self.frontend = self.theme((jp.Div), a=(self.html), classes='h-screen w-screen inset-0 absolute select-none')
        row_holder = self.theme((jp.Div), a=(self.frontend), classes='flex flex-row')
        l_placeholder = self.theme((jp.Div), a=row_holder, classes='flex-grow')
        row = self.theme((jp.Div), a=row_holder, classes='flex-grow-0')
        r_placeholder = self.theme((jp.Div), a=row_holder, classes='flex-grow')
        col_holder = self.theme((jp.Div), a=row, classes='flex flex-col justify-between')
        t_placeholder = self.theme((jp.Div), a=col_holder, classes='flex-grow sm:h-16 md:h-24 lg:h-32 xl:h-48')
        col = self.theme((jp.Div), a=col_holder, classes='flex-grow-0')
        b_placeholder = self.theme((jp.Div), a=col_holder, classes='flex-grow')
        login_form = self.stheme('form', (jp.Div), a=col_holder, classes='self-center flex flex-col justify-center')
        drow1 = self.theme((jp.Div), a=login_form, classes='flex flex-row')
        dl1 = self.theme((jp.Div), a=drow1, classes='flex-grow-0')
        self.lang_selector = self.stheme(None, LanguageSelector, dl1)
        c_placeholder = self.theme((jp.Div), a=drow1, classes='flex-grow')
        dr1 = self.theme((jp.Div), a=drow1, classes='flex-grow-0')
        close_form_button = self.stheme('form_close_button', (jp.Button), text='X', a=dr1, classes='-- w-auto -p-1 pl-2 pr-2 pt-0 pb-0 transition duration-250 ease-in-out font-bold transform hover:scale-125 hover:translate-y-0 hover:font-normal')
        close_form_button.on('click', self.on_close_form)
        head = self.stheme('form_head', (jp.Div), a=login_form, classes='select-none text-base mt-2 ml-2 mr-2 p-1 font-bold rounded-t border-b')
        self.jp_set_text(head, '{}', tt('Login Form'))
        form1 = jp.Form(a=login_form, classes='m-5 p-3 font-bold w-64')
        user_label = self.stheme('user_name_label', (jp.Label), classes='block uppercase tracking-wide mb-2', a=form1)
        self.jp_set_text(user_label, '{}', tt('User Name'))
        in1 = self.stheme('user_name_input', (jp.Input), a=form1, classes='form-input')
        self.jp_set_placeholder(in1, '{}', tt('User Name'))
        user_label.for_component = in1
        password_label = self.stheme('user_password_label', (jp.Label), classes='block uppercase tracking-wide mb-2 mt-2', a=form1)
        pass_div = jp.Div(classes='block uppercase tracking-wide text-gray-400 text-xs font-bold mb-2', a=password_label)
        self.jp_set_text(pass_div, '{}', tt('Password'))
        in2 = self.stheme('user_password_input', (jp.Input), a=password_label, classes='form-input text-base', type='password')
        self.jp_set_placeholder(in2, '{}', tt('Password'))
        check_label = self.stheme('send_stuff_label', (jp.Label), classes='block', a=form1)
        self.stheme('send_stuff_checkbox', (jp.Input), type='checkbox', a=check_label, classes='form-checkbox')
        send_stuff_span = jp.Span(a=check_label, classes='ml-2 text-gray-400 font-normal')
        self.jp_set_text(send_stuff_span, '{}', tt('Send me stuff'))
        submit_button = self.stheme('form_submit_button', (jp.Input), type='submit', a=form1, classes='self-center', forced_theme=(jp.Button))
        self.jp_set_value(submit_button, '{}', tt('Submit Form'))
        form1.on('submit', self.on_submit_form)

    @coro_event_handler()
    def on_close_form(i: Interface, self, item, msg):
        print('on_close_form:')
        pprint(str(msg))
        self.remove()
        self.delete()

    @coro_event_handler()
    def on_submit_form(i: Interface, self, item, msg):
        print('on_submit_form:')
        pprint(str(msg))
        self.remove()
        self.delete()

    def delete_impl(self, i: Interface):
        print('delete_impl...')
        self.html.delete()
        self.background.delete()
        self.lang_selector.delete()
        print('delete_impl.')


class Progressbar(CoroComponent):

    def init(self, max_progress: float, initial_progress: float):
        self.progress_bar = None
        self.max_progress = max_progress
        self.progress = self._calc_progress(max_progress, initial_progress)

    def _calc_progress(self, max_progress: float, progress: float) -> int:
        if progress < 0:
            progress = 0
        if progress > max_progress:
            progress = max_progress
        return int(round(100 * (progress / max_progress)))

    def set_progress(self, progress: float):
        self.progress = self._calc_progress(self.max_progress, progress)
        self.progress_bar.style = f"width:{self.progress}%"
        self.update_jp_item(self.progress_bar)

    def construct(self, root: Node):
        with root().subc('html', (jp.Div), classes='relative pt-1') as div:
            self.html = div.item
            with div()((jp.Div), classes='overflow-hidden h-2 mb-4 text-xs flex rounded bg-pink-200') as div:
                self.progress_bar = div()((jp.Div), classes='shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-pink-500', style=f"width:{self.progress}%", dynamic=True).item
                self.progress_bar.add_page(self.jp_web_page)


class AvailableComputingPower(CoroComponent):
    counter_started = False

    def init(self, default_text: str):
        self.default_text = default_text
        self.io_loop = self.interface(AsyncioLoop, AsyncioLoopRequest().get())
        self.pview = None
        self.ticks_num = 0
        self.dtime_list = list()
        self.update_stat_per_time = 1.0
        self.last_update_stat_time = None
        self.last_ticks_num = self.ticks_num

    def counter(self, interface):
        web_page_is_alive = self.web_page_is_alive_check()
        while True:
            before_yield = perf_counter()
            interface(Yield)
            if not web_page_is_alive():
                break
            else:
                self.ticks_num += 1
                after_yield = perf_counter()
                dtime = after_yield - before_yield
                self.dtime_list.append(dtime)
                self.update_stat()

    def update_stat(self):
        if self.last_update_stat_time is None:
            self.last_update_stat_time = perf_counter()
        current_time = perf_counter()
        tdiff = current_time - self.last_update_stat_time
        if tdiff >= self.update_stat_per_time:
            self.update_stat_impl(tdiff)
            self.last_update_stat_time = current_time

    def update_stat_impl(self, tdiff):
        dticks = self.ticks_num - self.last_ticks_num
        self.last_ticks_num = self.ticks_num
        ticks_per_second = dticks / tdiff
        required_stat_items = int(ceil(2 * ticks_per_second))
        dtime_list_len = len(self.dtime_list)
        items_to_be_deleted = dtime_list_len - required_stat_items
        if 0 < items_to_be_deleted:
            self.dtime_list = self.dtime_list[items_to_be_deleted:]
            self.update_stat_text(ticks_per_second)

    def update_stat_text(self, ticks_per_second):
        stat_template = 'val_99: {}; val_95: {}; val_68: {}; max_deviation: {}; min_deviation: {}'
        stat_text = str()
        try:
            stat_text = (stat_template.format)(*count_99_95_68(self.dtime_list, max))
        except:
            self.interface(SomePrinter, sys.exc_info())

        ptemplate = 'Yields per second: {}; Stat: <{}>'
        ptext = ptemplate.format(ticks_per_second, stat_text)
        self.pview.text = ptext
        create_task(self.io_loop, self.pview.update)

    def construct(self, root: Node):
        with root()((jp.P), dynamic=True, text=(self.default_text)) as pview:
            self.pview = pview.item
            self.pview.add_page(self.jp_web_page)
        if not AvailableComputingPower.counter_started:
            AvailableComputingPower.counter_started = True
            self.interface(PutCoro, self.counter)


class Tooltip(CoroComponent):

    class Positioning(Enum):
        right = 0
        left = 1
        top = 2
        bottom = 3

    def init(self, positioning: Positioning, text: Optional[Union[(str, TMe)]]=None):
        self.positioning = positioning
        self.tooltip_text = text
        self.wp_css = '\n.tooltip {\n  position: relative;\n  display: inline-block;\n}\n\n.tooltip .tooltiptext-right {\n  visibility: hidden;\n  /* Position the tooltip */\n  position: absolute;\n  z-index: 1;\n  top: -5px;\n  left: 105%;\n  margin-left: 0.25rem;\n}\n\n.tooltip .tooltiptext-right::after {\n  content: "";\n  position: absolute;\n  top: 50%;\n  right: 100%;\n  margin-top: -5px;\n  border-width: 5px;\n  border-style: solid;\n  border-color: transparent black transparent transparent;\n}\n\n.tooltip:hover .tooltiptext-right {\n  visibility: visible;\n}\n\n.tooltip .tooltiptext-left {\n  visibility: hidden;\n  /* Position the tooltip */\n  position: absolute;\n  z-index: 1;\n  top: -5px;\n  right: 105%;\n  margin-right: 0.25rem;\n}\n\n.tooltip .tooltiptext-left::after {\n  content: "";\n  position: absolute;\n  top: 50%;\n  left: 100%;\n  margin-top: -5px;\n  border-width: 5px;\n  border-style: solid;\n  border-color: transparent transparent transparent black;\n}\n\n.tooltip:hover .tooltiptext-left {\n  visibility: visible;\n}\n\n.tooltip .tooltiptext-top {\n  visibility: hidden;\n  /* Position the tooltip */\n  position: absolute;\n  z-index: 1;\n  bottom: 100%;\n  left: 50%;\n  margin-left: -60px;\n  margin-bottom: 0.25rem;\n}\n\n.tooltip .tooltiptext-top::after {\n  content: "";\n  position: absolute;\n  top: 100%;\n  left: 50%;\n  margin-left: -5px;\n  border-width: 5px;\n  border-style: solid;\n  border-color: black transparent transparent transparent;\n}\n\n.tooltip:hover .tooltiptext-top {\n  visibility: visible;\n}\n\n.tooltip .tooltiptext-bottom {\n  visibility: hidden;\n  /* Position the tooltip */\n  position: absolute;\n  z-index: 1;\n  top: 100%;\n  left: 50%;\n  margin-left: -60px;\n  margin-top: 0.25rem;\n}\n\n.tooltip .tooltiptext-bottom::after {\n  content: "";\n  position: absolute;\n  bottom: 100%;\n  left: 50%;\n  margin-left: -5px;\n  border-width: 5px;\n  border-style: solid;\n  border-color: transparent transparent black transparent;\n}\n\n.tooltip:hover .tooltiptext-bottom {\n  visibility: visible;\n}\n'
        self.wp_css = self.wp_css.strip()

    def construct(self, root: Node):
        if Tooltip.Positioning.right == self.positioning:
            tooltiptext_class = 'tooltiptext-right'
        else:
            if Tooltip.Positioning.left == self.positioning:
                tooltiptext_class = 'tooltiptext-left'
            else:
                if Tooltip.Positioning.top == self.positioning:
                    tooltiptext_class = 'tooltiptext-top'
                else:
                    if Tooltip.Positioning.bottom == self.positioning:
                        tooltiptext_class = 'tooltiptext-bottom'
        if self.tooltip_text is None:
            self.container = self.html = root().subc('container', (jp.Span), classes=(f"{tooltiptext_class}")).item
        else:
            self.container = self.html = root().subc('container_with_text', (jp.Span), text=(self.tooltip_text), classes=(f"{tooltiptext_class}")).item
        jp_parent = jp_entity_from_parent_link(root.parent)
        if not jp_parent is not None or isinstance(jp_parent, jp.HTMLBaseComponent) or isinstance(jp_parent, jp.WebPage):
            uc(self.args_manager, jp_parent, 'tooltip', gft(self.args_manager, jp_parent))
        else:
            raise RuntimeError(f"Unsupported item_type: {type(jp_parent)}; of value: {jp_parent}")
        if self.wp_css not in self.wp.css:
            if self.wp.css is None:
                self.wp.css = self.wp_css
            else:
                self.wp.css = f"{self.wp.css}\n{self.wp_css}"


class HelpString(CoroComponent):

    def init(self, tooltip_text):
        self.tooltip_text = tooltip_text

    def construct(self, root: Node):
        jp_target = None
        if root.parent is not None:
            parent = root.parent.parent
            parent_container_id = root.parent.parent_container_id
            if isinstance(parent, Component):
                jp_target
                if isinstance(parent, Component):
                    jp_target = parent.container_by_id(parent_container_id)
                else:
                    jp_target = parent
        with root().subc('html', (jp.Div), classes='relative pt-1') as div:
            self.html = div.item
            with div()((jp.Div), classes='overflow-hidden h-2 mb-4 text-xs flex rounded bg-pink-200') as div:
                self.progress_bar = div()((jp.Div), classes='shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-pink-500', style=f"width:{self.progress}%", dynamic=True).item
                self.progress_bar.add_page(self.jp_web_page)


class UserAgentIndicator(CoroComponent):

    def init(self, request):
        self.user_agent = request.headers['user-agent']

    def construct(self, root: Node):
        root().subc('html', (jp.Div), text=(self.user_agent), classes='text-5xl sm:text-4xl md:text-3xl lg:text-2xl xl:text-xl 2xl:text-lg')


class DetectMetaSize(CoroComponent):

    def init(self, callback):
        self.callback = callback
        self.media_info = None
        self.request_id = str(uuid.uuid4())
        self.js_func = 'function getViewport() {\n\n var viewPortWidth;\n var viewPortHeight;\n\n // the more standards compliant browsers (mozilla/netscape/opera/IE7) use window.innerWidth and window.innerHeight\n if (typeof window.innerWidth != \'undefined\') {\n   viewPortWidth = window.innerWidth,\n   viewPortHeight = window.innerHeight\n }\n\n// IE6 in standards compliant mode (i.e. with a valid doctype as the first line in the document)\n else if (typeof document.documentElement != \'undefined\'\n && typeof document.documentElement.clientWidth !=\n \'undefined\' && document.documentElement.clientWidth != 0) {\n    viewPortWidth = document.documentElement.clientWidth,\n    viewPortHeight = document.documentElement.clientHeight\n }\n\n // older versions of IE\n else {\n   viewPortWidth = document.getElementsByTagName(\'body\')[0].clientWidth,\n   viewPortHeight = document.getElementsByTagName(\'body\')[0].clientHeight\n }\n return [viewPortWidth, viewPortHeight];\n}\n\nfunction getDevicePixelRatio() {\n    var mediaQuery;\n    var is_firefox = navigator.userAgent.toLowerCase().indexOf(\'firefox\') > -1;\n    if (window.devicePixelRatio !== undefined && !is_firefox) {\n        return window.devicePixelRatio;\n    } else if (window.matchMedia) {\n        mediaQuery = "(-webkit-min-device-pixel-ratio: 1.5),          (min--moz-device-pixel-ratio: 1.5),          (-o-min-device-pixel-ratio: 3/2),          (min-resolution: 1.5dppx)";\n        if (window.matchMedia(mediaQuery).matches) {\n            return 1.5;\n        }\n        mediaQuery = "(-webkit-min-device-pixel-ratio: 2),          (min--moz-device-pixel-ratio: 2),          (-o-min-device-pixel-ratio: 2/1),          (min-resolution: 2dppx)";\n        if (window.matchMedia(mediaQuery).matches) {\n            return 2;\n        }\n        mediaQuery = "(-webkit-min-device-pixel-ratio: 0.75),          (min--moz-device-pixel-ratio: 0.75),          (-o-min-device-pixel-ratio: 3/4),          (min-resolution: 0.75dppx)";\n        if (window.matchMedia(mediaQuery).matches) {\n            return 0.7;\n        }\n    } else {\n        return 1;\n    }\n}\n\nfunction getPixelRatio() {\n    dpr = undefined\n    try {\n        dpr = window.devicePixelRatio;\n    } catch (exv) {};\n    \n    if (dpr === undefined) {\n        try {\n            dpr = window.screen.deviceXDPI / window.screen.logicalXDPI;\n        } catch (exv) {};\n    };\n    \n    if (dpr === undefined) {\n        try {\n            dpr = getDevicePixelRatio();\n        } catch (exv) {};\n    };\n    \n    if (dpr === undefined) {\n        dpr = 1\n    };\n    \n    return dpr;\n}\n\n[getViewport(), getPixelRatio()]'

    def get_request_id(self):
        self.request_id = str(uuid.uuid4())
        return self.request_id

    def construct(self, root: Node):
        app = cast(JpRunner, self.jp_web_page.application_instance)

        def meta_viewport_getter(interface: Interface, self):

            async def a_meta_viewport_getter(jp_web_page):
                request_id = self.get_request_id()
                await jp_web_page.run_javascript((self.js_func), request_id=request_id)

            create_task(self.asyncio_loop, a_meta_viewport_getter, self.jp_web_page)

        async def on_page_ready_handler(*args, **kwargs):
            await self.await_task_fast(PutCoro, meta_viewport_getter, self)

        async def on_result_ready_handler(wp, msg, event_name, handler_id):
            if msg['request_id'] == self.request_id:
                app.remove_on_page_event(self.jp_web_page.page_id, 'result_ready', handler_id)
                if self.callback is not None:
                    if is_async(self.callback):
                        await self.callback(self.dimentions)
                    else:
                        if is_callable(self.callback):
                            self.callback(self.dimentions)

        app.add_on_page_event(self.jp_web_page.page_id, 'page_ready', on_page_ready_handler)
        app.add_on_page_event(self.jp_web_page.page_id, 'result_ready', on_result_ready_handler)


class MetaSizeIndicator(CoroComponent):

    def init(self):
        self.request_id = str(uuid.uuid4())
        self.indicator = None

    def get_request_id(self):
        self.request_id = str(uuid.uuid4())
        return self.request_id

    def construct(self, root: Node):
        self.indicator = root().subc('html', (jp.Div), text='MetaSizeIndicator', classes='bg-white sm:bg-red-500 md:bg-yellow-500 lg:bg-green-500 xl:bg-blue-500 2xl:bg-gray-500 text-5xl sm:text-4xl md:text-xl lg:text-2xl xl:text-xl 2xl:text-base', dynamic=True).item
        self.indicator.add_page(self.jp_web_page)

        async def callback(media_info):
            self.indicator.text = f"MetaSizeIndicator: {media_info}"
            await self.indicator.update()

        root()(DetectMetaSize, callback)


class DetectDeviceScreenSizes(CoroComponent):

    def init(self, callback=None):
        self.callback = callback
        self.dimentions = None
        self.request_id = str(uuid.uuid4())
        self.indicator = None
        self.js_func = 'function getDeviceScreenSizes() {\n    var indicator_id = "{%indicator_id%}";\n    var indicator = document.getElementById(indicator_id);\n    var dpi_x = indicator.offsetWidth;\n    var dpi_y = indicator.offsetHeight;\n    var width = screen.width / dpi_x;\n    var height = screen.height / dpi_y;\n\n    return [width, height, screen.width, screen.height, dpi_x, dpi_y];\n}\n\ngetDeviceScreenSizes()'

    def get_request_id(self):
        self.request_id = str(uuid.uuid4())
        return self.request_id

    def construct(self, root: Node):
        self.indicator = root().subc('html', (jp.Div), style='height: 1in; width: 1in; left: 100%; position: fixed; top: 100%;', classes='--', dynamic=True).item
        self.indicator.add_page(self.jp_web_page)
        indicator_id = str(self.indicator.id)
        js_func = self.js_func.replace('{%indicator_id%}', indicator_id)
        app = cast(JpRunner, self.jp_web_page.application_instance)

        def meta_viewport_getter(interface, self):

            async def a_meta_viewport_getter(jp_web_page):
                request_id = self.get_request_id()
                await jp_web_page.run_javascript(js_func, request_id=request_id)

            create_task(self.asyncio_loop, a_meta_viewport_getter, self.jp_web_page)

        async def on_page_ready_handler(*args, **kwargs):
            await self.await_task_fast(PutCoro, meta_viewport_getter, self)

        async def on_result_ready_handler(wp, msg, event_name, handler_id):
            if msg['request_id'] == self.request_id:
                pprint(f"DetectDeviceScreenSizes result: {msg}")
                width, height, screen_width, screen_height, dpi_x, dpi_y = msg['result']
                print(width, height, screen_width, screen_height, dpi_x, dpi_y)
                self.dimentions = (sqrt(width ** 2 + height ** 2), width, height, screen_width, screen_height, dpi_x, dpi_y)
                print(f"DetectDeviceScreenSizes Dimentions: {self.dimentions}")
                app.remove_on_page_event(self.jp_web_page.page_id, 'result_ready', handler_id)
                if self.callback is not None:
                    if is_async(self.callback):
                        await self.callback(self.dimentions)
                    else:
                        if is_callable(self.callback):
                            self.callback(self.dimentions)

        app.add_on_page_event(self.jp_web_page.page_id, 'page_ready', on_page_ready_handler)
        app.add_on_page_event(self.jp_web_page.page_id, 'result_ready', on_result_ready_handler)


class DeviceScreenSizesIndicator(CoroComponent):

    def init(self):
        self.request_id = str(uuid.uuid4())
        self.indicator = None

    def get_request_id(self):
        self.request_id = str(uuid.uuid4())
        return self.request_id

    def construct(self, root: Node):
        self.indicator = root().subc('html', (jp.Div), text='DeviceScreenSizesIndicator', classes='bg-white sm:bg-red-500 md:bg-yellow-500 lg:bg-green-500 xl:bg-blue-500 2xl:bg-gray-500 text-5xl sm:text-4xl md:text-3xl lg:text-2xl xl:text-xl 2xl:text-lg', dynamic=True).item
        self.indicator.add_page(self.jp_web_page)

        async def callback(dimentions):
            self.indicator.text = f"DeviceScreenSizesIndicator: {dimentions}"
            await self.indicator.update()

        root()(DetectDeviceScreenSizes, callback)