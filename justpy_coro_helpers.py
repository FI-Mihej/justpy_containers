__all__ = [
 'jp_coro_interfaces_arg_manager','CoroComponent','coro_event_handler','create_justpy_args_manager','create_component_args_manager','JpRunner','page']
from collections import UserDict
from cengal.code_flow_control import args_manager
from cengal.parallel_execution.coroutines import coro_interfaces_arg_manager as ciam, CoroScheduler
from cengal.parallel_execution.coroutines.coro_scheduler import CoroScheduler, CoroType, Worker, Interface, available_coro_scheduler, set_primary_coro_scheduler, current_coro_scheduler
from cengal.parallel_execution.coroutines.coro_tools.await_coro.versions.v_0.await_coro import await_coro, await_coro_fast, RunSchedulerInAsyncioLoop
from cengal.parallel_execution.coroutines.coro_standard_services.loop_yield import *
from cengal.parallel_execution.coroutines.coro_standard_services.log import *
from cengal.parallel_execution.coroutines.coro_standard_services.asyncio_loop import *
from cengal.parallel_execution.coroutines.coro_standard_services.lmdb import *
from cengal.file_system.file_manager import path_relative_to_current_src
import cengal.RequestCache as RequestCache
from cengal.introspection.inspect import get_exception
from justpy.htmlcomponents import Option
from low_latency_justpy import justpy, init_scheduler, init_thread_pool_executor
from justpy_components import *
from starlette.requests import Request
from cengal.code_flow_control.args_manager import ArgsManager, EArgs, EntityWithExtendableArgs
from cengal.text_processing.text_translator import *
import random
from typing import Callable, Hashable, Optional, Tuple, Union, Type, Dict, Any, Coroutine, Set
import inspect
from pprint import pprint
from inspect import iscoroutinefunction, ismethod

def jp_coro_interfaces_arg_manager(coro_scheduler: CoroScheduler):
    return ciam(justpy.asyncio.get_event_loop(), coro_scheduler)


class CoroComponent(Component):

    def __init__(self, *args, **kwargs):
        self.await_coro_fast = None
        self.await_task_fast = None
        self.i = self.interface
        (super().__init__)(*args, **kwargs)

    def _init(self, parent, jp_web_page, await_coro_fast, await_task_fast, theme_applier=None, ly=None, args_manager=None, theme=None, text_translation_reapplier=None, classes=None):
        self.await_coro_fast = await_coro_fast
        self.await_task_fast = await_task_fast
        super()._init(parent=parent, jp_web_page=jp_web_page, theme_applier=theme_applier, ly=ly, args_manager=args_manager, theme=theme, text_translation_reapplier=text_translation_reapplier, classes=classes)
        if args_manager is None:
            self.args_manager.append(EArgs(await_coro_fast=(self.await_coro_fast), await_task_fast=(self.await_task_fast)))
        gly(CoroPriority.low)()

    def update_web_page(self):
        current_coro_scheduler().current_coro_interface(AsyncioLoop, AsyncioLoopRequest().wait(self.jp_web_page.update()))

    def update_jp_item(self, jp_item: JPContainer):
        current_coro_scheduler().current_coro_interface(AsyncioLoop, AsyncioLoopRequest().wait(jp_item.update()))

    @property
    def interface(self):
        return current_coro_scheduler().current_coro_interface


def coro_event_handler(catch_child_events: bool=False, page_update: Tuple[(bool, bool)]=(False, False)):

    def real_decorator(coro):

        async def coro_executor(self_or_item, *args, **kwargs):
            if is_msg_processing_allowed(catch_child_events, coro, self_or_item, *args, **kwargs):
                if isinstance(self_or_item, CoroComponent):
                    if page_update[0]:
                        await self_or_item.jp_web_page.update()
                    await (self_or_item.await_coro_fast)(coro, self_or_item, *args, **kwargs)
                    if page_update[1]:
                        await self_or_item.jp_web_page.update()
                else:
                    _, msg = find_msg_in_args_kwargs(self_or_item, *args, **kwargs)
                    if page_update[0]:
                        await msg.page.update()
                    await await_coro_fast(justpy.asyncio.get_event_loop(), available_coro_scheduler(), CoroType.auto, coro, self_or_item, *args, **kwargs)
                    if page_update[1]:
                        await msg.page.update()

        return coro_executor

    return real_decorator


def create_justpy_args_manager(theme_args_manager: ThemeArgsManager, jp_creation_time_translation: JpCreationTimeTranstation) -> ArgsManager:
    return ArgsManager(theme_args_manager, jp_creation_time_translation).add_interceptor(theme_args_manager.interception).add_interceptor(jp_creation_time_translation.interception)


def create_component_args_manager(theme_args_manager: ThemeArgsManager, cs: CoroScheduler, text_translation_reapplier: TextTranslationReapplier, wp: justpy.WebPage, jp_creation_time_translation: JpCreationTimeTranstation, ly: Union[(LoopYieldManaged, FakeLoopYieldManaged)]) -> ArgsManager:
    am = ArgsManager(theme_args_manager, jp_coro_interfaces_arg_manager(cs), jp_creation_time_translation, EArgs(text_translation_reapplier=text_translation_reapplier), EArgs(jp_web_page=wp), EArgs(ly=ly))
    am.append(EArgs(args_manager=am))
    am.add_interceptor(theme_args_manager.interception)
    am.add_interceptor(jp_creation_time_translation.interception)
    return am


def determine_user_language(request: Request) -> str:
    accept_language = request.headers['accept-language']
    lang_list = accept_language.split(',')
    lang_list_buf = lang_list
    lang_list = type(lang_list)()
    for lang in lang_list_buf:
        if not lang.startswith('q='):
            lang_list.append(lang)

    if lang_list:
        return lang_list[0][:2]
    return


AppSettings = Dict[(str, Union[(Dict, Set, str, int, float)])]

class JpRunner:

    def __init__(self):
        self.main_loop = None
        self.cs = None
        self.rs = None
        self.text_translator = None
        self.translation_language_mapper = None
        self._main_page = None
        self._themes = dict()
        self.user_data = dict()
        self.session_data = dict()
        self.page_data = dict()
        self.user_sessions = dict()
        self.session_pages = dict()
        self.user_by_session = dict()
        self.session_by_page = dict()
        routes = self.return_routes()
        if routes is not None:
            self._main_page, pages = routes
            if pages is not None:
                for route_path, page in pages.items():
                    justpy.Route(route_path, page)

        self.init()

    def init(self):
        pass

    def on_page_removed(self, page_id, session_id, user_id):
        pass

    def on_session_removed(self, session_id, user_id):
        if user_id is None:
            if session_id is not None:
                key = ''.join('session_settings||', session_id)
                value = {'_base': self.session_data[session_id]['_base']}
                self.cs.current_interface()(Lmdb, LmdbRequest().put(key, value))

    def on_user_removed(self, user_id):
        key = ''.join('user_settings||', user_id)
        value = {'_base': self.session_data[user_id]['_base']}
        self.cs.current_interface()(Lmdb, LmdbRequest().put(key, value))

    def cs_setup_impl(self, cs: CoroScheduler):
        pass

    def cs_services_setup_impl(self, interface: Interface):
        pass

    def return_is_async_page_generation_required(self) -> bool:
        return True

    def return_host(self) -> Optional[str]:
        pass

    def return_port(self) -> Optional[int]:
        pass

    def return_justpy_kwargs(self) -> Dict:
        return dict()

    def return_web_page_body_classes(self, request: Request) -> str:
        return str()

    def return_web_page_class(self, request: Request) -> justpy.WebPage:
        return justpy.WebPage

    def return_path_to_log_dir(self) -> str:
        return path_relative_to_current_src('default_log_dir_name')

    def return_path_to_sessions_dir(self) -> str:
        return path_relative_to_current_src('default_sessions_dir_name')

    def return_yield_priority_scheduler_max_delay(self) -> float:
        return 0.001

    def return_scheduler_idle_time(self) -> float:
        return 0.02

    async def return_text_dictionary(self) -> str:
        return '{\n    "type": "Cengal.TextTranslationDictionary",\n    "version": "1.0.0",\n    "text_translation_list": [\n    ]\n}'

    async def return_translation_language_map(self) -> Dict:
        return {'en': 'en'}

    async def return_default_language(self) -> str:
        return 'en'

    def return_routes(self) -> Tuple[(Callable, Dict[(str, Callable)])]:
        pass

    async def on_disconnect_handler(self, wp: justpy.WebPage, will_be_removed: bool) -> None:
        pass

    def on_remove_handler(self, wp: justpy.WebPage) -> None:
        pass

    def register_theme(self, theme_id: Hashable, theme: Theme):
        self._themes[theme_id] = theme

    def get_theme(self, theme_id: Hashable) -> Theme:
        return self._themes[theme_id]

    def return_default_theme_id(self) -> Hashable:
        raise NotImplementedError

    def return_page_theme_args_manager(self, request: Request, theme_args_manager: ThemeArgsManager) -> ThemeArgsManager:
        pass

    async def startup_impl(self):
        pass

    def renderer(self, interface: Interface, web_page: justpy.WebPage, theme: Callable, request: Request):
        pass

    def current_settings(self, session_id, user_id) -> AppSettings:
        if user_id is None:
            if session_id is None:
                return dict()
            return self.session_data[session_id]
        else:
            return self.user_data[user_id]

    def current_page_settings(self, page_id) -> AppSettings:
        session_id = self.session_by_page[page_id]
        user_id = self.user_by_session.get(session_id, None)
        if user_id is None:
            return self.session_data[session_id]
        return self.user_data[user_id]

    def actualize_current_settings(self, current_settings_holder: AppSettings, session_id, user_id):
        current_settings_holder['_base']['translation.language'] = current_settings_holder['_objects']['text_translation_reapplier'].text_translator.lang

    def try_restore_session_settings(self, session_id) -> Dict:
        key = f"session_settings||{session_id}"
        try:
            return self.cs.current_interface()(Lmdb, LmdbRequest().get(key))
        except KeyError:
            return dict()

    def try_restore_user_settings(self, user_id) -> Dict:
        key = f"user_settings||{user_id}"
        try:
            return self.cs.current_interface()(Lmdb, LmdbRequest().get(key))
        except KeyError:
            return dict()

    def move_settings_from_session_to_user(self, session_id, user_id):
        """We should update user settings with session settings which was changed from defaults by user actions (not automatically)
        In this case we can update for example required language and theme and us them even after login

        Args:
            session_id ([type]): [description]
            user_id ([type]): [description]
        """
        self.actualize_current_settings(self.session_data, session_id, user_id)
        if '_base' not in self.user_data[user_id]:
            self.user_data[user_id]['_base'] = self.session_data[session_id]['_base']
        if '_objects' not in self.user_data[user_id]:
            self.user_data[user_id]['_objects'] = self.session_data[session_id]['_objects']

    def move_settings_from_user_to_settings(self, session_id, user_id):
        """We should move only settings applicable for the logged out session. No personal data (user name, user accesses, etc.) should be moved to the session settings

        Args:
            session_id ([type]): [description]
            user_id ([type]): [description]
        """
        self.session_data[session_id] = self.user_data[user_id]

    def _register_session(self, session_id) -> Optional[str]:
        if session_id is None:
            return
        if session_id not in self.session_data:
            self.session_data[session_id] = self.try_restore_session_settings(session_id)
        return self.user_by_session.get(session_id, None)

    def _register_page(self, page_id, session_id):
        self.page_data[page_id] = dict()
        if session_id is None:
            return
        if session_id not in self.session_pages:
            self.session_pages[session_id] = set()
        self.session_pages[session_id].add(page_id)
        self.session_by_page[page_id] = session_id

    def login_sesion(self, session_id, user_id) -> bool:
        if session_id is None:
            return False
        if user_id not in self.user_data:
            self.user_data[user_id] = self.try_restore_user_settings(user_id)
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)
        self.user_by_session[session_id] = user_id
        self.move_settings_from_session_to_user(session_id, user_id)
        return True

    def logout_session(self, session_id) -> bool:
        if session_id is None:
            return False
        user_id = self.user_by_session.get(session_id, None)
        if user_id is None:
            return False
        del self.user_by_session[session_id]
        self.user_sessions[user_id].remove(session_id)
        user_will_be_removed = False
        if not self.user_sessions[user_id]:
            user_will_be_removed = True
            del self.user_sessions[user_id]
        self.move_settings_from_user_to_settings(session_id, user_id)
        if user_will_be_removed:
            self.on_user_removed(user_id)
            del self.user_data[user_id]
        return True

    def get_tokens_from_msg(self, msg):
        page_id, session_id = justpy.get_tokens_from_msg(msg)
        user_id = self.user_by_session.get(session_id, None)
        return (
         page_id, session_id, user_id)

    def _disconnected_page(self, page_id):
        session_id = self.session_by_page[page_id]
        user_id = self.user_by_session.get(session_id, None)
        if user_id is None:
            if session_id is None:
                current_settings = dict()
            else:
                current_settings = self.session_data[session_id]
        else:
            current_settings = self.user_data[user_id]
        self.actualize_current_settings(current_settings, page_id, session_id, user_id)
        self.on_page_removed(page_id, session_id, user_id)
        del self.page_data[page_id]
        del self.session_by_page[page_id]
        self.session_pages[session_id].remove(page_id)
        session_will_be_removed = False
        if not self.session_pages[session_id]:
            session_will_be_removed = True
            del self.session_pages[session_id]
        if session_will_be_removed:
            self.on_session_removed(session_id, user_id)
            del self.session_data[session_id]
        user_will_be_removed = False
        if not user_id is not None or session_will_be_removed:
            del self.user_by_session[session_id]
            self.user_sessions.remove(session_id)
            if not self.user_sessions[user_id]:
                user_will_be_removed = True
                del self.user_sessions[user_id]
            if user_will_be_removed:
                self.on_user_removed(user_id)
                del self.user_data[user_id]

    def _prepare_text_translation_reapplier(self, language: str) -> TextTranslationReapplier:
        translation_language_chooser = TranslationLanguageChooser((self.text_translator),
          (self.translation_language_mapper),
          coro_scheduler=(self.cs))
        translation_language_chooser.lang = language
        return TextTranslationReapplier(translation_language_chooser)

    async def _startup(self):
        self.main_loop = justpy.asyncio.get_event_loop()

        def cs_services_setup(interface):
            interface(LoopYieldPriorityScheduler, LoopYieldPrioritySchedulerRequest().setup(self.return_yield_priority_scheduler_max_delay()))
            interface(Log, LogRequest().set_db_environment_path(self.return_path_to_log_dir()))
            interface(Lmdb, LmdbRequest().set_db_environment_path(self.return_path_to_sessions_dir()))
            interface(AsyncioLoop, AsyncioLoopRequest().set(self.main_loop))
            self.cs_services_setup_impl(interface)

        if self.cs is None:
            self.cs = CoroScheduler()
            self.cs.turn_on_embedded_mode(True)
            set_primary_coro_scheduler(self.cs)
            self.cs.get_service_instance(Lmdb).default_db_name = b'data'
            self.cs.set_coro_time_measurement(True)
            self.cs_setup_impl(self.cs)
        if self.return_is_async_page_generation_required():
            init_scheduler(CoroPriority.high, self.cs, self.main_loop)
        if self.rs is None:
            self.rs = RunSchedulerInAsyncioLoop(self.cs, self.return_scheduler_idle_time(), self.main_loop)
            self.rs.register()
        await await_coro_fast(self.main_loop, self.cs, CoroType.auto, cs_services_setup)
        if self.text_translator is None:
            self.text_translator = TextTranslator.from_json(await self.return_text_dictionary())
        if self.translation_language_mapper is None:
            self.translation_language_mapper = TranslationLanguageMapper(await self.return_translation_language_map(), await self.return_default_language())
        random.seed()
        await self.startup_impl()

    async def _main_page_impl(self, request: Request):
        session_id = request.session_id
        translation_language_chooser = TranslationLanguageChooser((self.text_translator),
          (self.translation_language_mapper),
          coro_scheduler=(self.cs))
        translation_language_chooser.lang = determine_user_language(request)
        text_translation_reapplier = TextTranslationReapplier(translation_language_chooser, CoroPriority.high)

        def renderer(interface, self):
            theme_args_manager = ThemeArgsManager(self.return_default_theme_id())
            jpam = create_justpy_args_manager(theme_args_manager)
            wp = jpam((self.return_web_page_class()), cs=(self.cs), body_classes=(self.return_web_page_body_classes()), delete_flag=False)
            page_id = wp.page_id
            coam = create_component_args_manager(theme_args_manager, self.cs, text_translation_reapplier, wp)
            am = ThemeApplier(coam, jpam, text_translation_reapplier)
            tokens = (page_id, session_id, None)
            self.renderer(interface, request, request, wp, am, tokens)
            return wp

        wp = await await_coro_fast(self.main_loop, self.cs, CoroType.auto, renderer, self)
        return wp

    def set_route(self, route_path: str, page: Callable):
        justpy.Route(route_path, page)

    def set_main_page(self, page: Callable):
        self._main_page = page

    def __call__(self):
        (justpy.justpy)(self._main_page, startup=self._startup, reload=True, host=self.return_host(), port=self.return_port(), **self.return_justpy_kwargs())


def page():

    def page_impl(renderer):

        async def page_wrapper(self, request):

            def renderer_wrapper(i, self, request):
                session_id = request.session_id
                user_id = self._register_session(session_id)
                current_settings = self.current_settings(session_id, user_id)
                settings_objects = current_settings.get('_objects', None)
                if settings_objects is None:
                    settings_base = current_settings.get('_base', None)
                    if settings_base is None:
                        language = determine_user_language(request)
                        theme_id = self.return_default_theme_id()
                        current_settings['_base'] = {'translation.language':language, 
                         'theme.theme_id':theme_id}
                        theme = self.get_theme(theme_id)
                    else:
                        language = settings_base['translation.language']
                        theme = self.get_theme(settings_base['theme.theme_id'])
                    text_translation_reapplier = self._prepare_text_translation_reapplier(language)
                    theme_args_manager = ThemeArgsManager(theme)
                    current_settings['_objects'] = {'text_translation_reapplier':text_translation_reapplier, 
                     'theme_args_manager':theme_args_manager}
                else:
                    text_translation_reapplier = settings_objects['text_translation_reapplier']
                    theme_args_manager = settings_objects['theme_args_manager']
                page_theme_args_manager = self.return_page_theme_args_manager(request, theme_args_manager)
                if page_theme_args_manager is not None:
                    theme_args_manager = page_theme_args_manager
                jp_creation_time_translation = JpCreationTimeTranstation(text_translation_reapplier)
                jpam = create_justpy_args_manager(theme_args_manager, jp_creation_time_translation)
                wp = jpam((self.return_web_page_class(request)), cs=(self.cs), body_classes=(self.return_web_page_body_classes(request)), delete_flag=False)
                page_id = wp.page_id
                self._register_page(page_id, session_id)
                wp.handler_on_disconnect = self.on_disconnect_handler
                wp.handler_on_remove = self.on_remove_handler
                ly = gly(CoroPriority.low)
                coam = create_component_args_manager(theme_args_manager, self.cs, text_translation_reapplier, wp, jp_creation_time_translation, ly)
                theme_applier = ThemeApplier(coam, jpam, text_translation_reapplier)
                coam.append(EArgs(theme_applier=theme_applier))
                node = Node(theme_applier, wp, None, ly)
                tokens = (page_id, session_id, user_id)
                wp.application_instance = self
                renderer(self, i, request, wp, node, tokens)
                return wp

            wp = await await_coro_fast(self.main_loop, self.cs, CoroType.auto, renderer_wrapper, self, request)
            return wp

        return page_wrapper

    return page_impl