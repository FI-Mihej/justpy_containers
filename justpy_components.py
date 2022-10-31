__all__ = [
 'AppBaseMixin','OnPageDestroySubscribeClient','ComponentsTreeUpdater','ThemeApplierMixin','ModifyClassesMixin','JpItemTranslationMixin','TranslateMe','TMe','JpCreationTimeTranstation','Container','SubContainer','JPContainer','UIElement','Theme','ClassesList','ItemClasses','ItemOrComponentThemeId','ComponentClasses','ItemType','SubComponentTheme','ThemeArgsManager','async_handle_runner','find_msg_in_args_kwargs','is_msg_processing_allowed','event_handler','Component','jp_init','jp_delete','jp_hide','jp_remove','jp_insert_to','jp_show','delete_component','hide_component','show_component','remove_component','insert_component_to','jp_set_text','jp_set_placeholder','jp_set_value','jp_set_href','jp_set_title','inode','tnode','INodeImpl','AImpl','set_classes','sc','get_forced_theme','gft','update_classes','uc','parent','ThemeApplier','ParentLink','NodeApplier','Node','WebPageIsAlive','jp_set_raw_classes','jp_ensure_update_web_page','HashCache','jp_entity_from_parent_link']
from multiprocessing import managers
from justpy.htmlcomponents import Option, travers_components_tree
from low_latency_justpy import justpy
import inspect, asyncio
from enum import Enum
from cengal.code_flow_control.args_manager import *
from cengal.text_processing.text_translator import *
from pprint import pprint
from typing import Union, Optional, Dict, List, Set, Tuple, Hashable, Sequence, Callable, Any, Type, cast
from cengal.parallel_execution.coroutines.coro_standard_services.loop_yield import *
from cengal.parallel_execution.coroutines.coro_tools.await_coro import create_task
from cengal.data_manipulation.performant_list_operations import remove_items_from_list
from contextlib import contextmanager
import copy, sys
from cengal.parallel_execution.coroutines.coro_scheduler import current_interface, CoroScheduler, CoroType, Worker, Interface, available_coro_scheduler, set_primary_coro_scheduler, current_coro_scheduler, Coro, CoroID
from cengal.code_flow_control.smart_values.versions.v_2 import ValueExistence
from frozendict import frozendict
from contextlib import contextmanager
from cengal.performance_test_lib import test_run_time
import gc
Container = Union[('Component', justpy.HTMLBaseComponent, justpy.WebPage)]
SubContainer = Union[('Component', justpy.HTMLBaseComponent)]
JPContainer = Union[(justpy.HTMLBaseComponent, justpy.WebPage)]
UIElement = Union[('Component', justpy.HTMLBaseComponent)]
Theme = Dict[(Type, Union[(List[str], str)])]
ClassesList = List[str]
ItemClasses = Union[(str, ClassesList)]
ItemOrComponentThemeId = str
ComponentClasses = Dict[(ItemOrComponentThemeId, Union[('ComponentClasses', ItemClasses)])]
ItemType = Union[(Type, 'SubComponentTheme')]

class AppBaseMixin:

    def add_on_page_removed_handler(self, page_id: Hashable, asyncio_coroutine_handler) -> Optional[Hashable]:
        raise NotImplementedError

    def remove_on_page_removed_handler(self, page_id: Hashable, handler_id: Hashable):
        raise NotImplementedError


class DifferentApplicationsInSingleWpSetError(Exception):
    pass


class OnPageDestroySubscribeClient:

    def __init__(self, wp: Optional[Union[(justpy.WebPage, Set[justpy.WebPage])]], external_on_page_removed_asyncio_coroutine_handler, external_on_destroy_asyncio_coroutine_handler) -> None:
        self.wp = wp
        self.external_on_page_removed_asyncio_coroutine_handler = external_on_page_removed_asyncio_coroutine_handler
        self.external_on_destroy_asyncio_coroutine_handler = external_on_destroy_asyncio_coroutine_handler
        self.on_page_removed_handlers = dict()
        self.app = None
        if isinstance(self.wp, justpy.WebPage):
            self.app = getattr(self.wp, 'application_instance', None)
            wp_page_id = self.wp.page_id
            self.on_page_removed_handlers[wp_page_id] = self.app.add_on_page_removed_handler_id(wp_page_id, self._handler_on_page_removed_impl)
        else:
            if isinstance(self.wp, set) and self.wp:
                for wp in self.wp:
                    if self.app is None:
                        self.app = getattr(wp, 'application_instance', None)
                    else:
                        if id(self.app) != id(getattr(wp, 'application_instance', None)):
                            raise DifferentApplicationsInSingleWpSetError
                        wp_page_id = wp.page_id
                        self.on_page_removed_handlers[wp_page_id] = self.app.add_on_page_removed_handler_id(wp_page_id, self._handler_on_page_removed_impl)

            else:
                pass
        self.destroyed = False

    async def _handler_on_page_removed_impl(self, page_id: Hashable, session_id: Hashable, user_id: Hashable):
        await self.external_on_page_removed_asyncio_coroutine_handler(page_id, session_id, user_id)
        if not self.on_page_removed_handlers:
            await self.destroy()

    async def destroy(self):
        if not self.destroyed:
            if self.app is not None:
                for wp_page_id, handler_id in self.on_page_removed_handlers.items():
                    self.app.remove_on_page_removed_handler_id(wp_page_id, handler_id)

            await self.external_on_destroy_asyncio_coroutine_handler()
            self._self_destroy()

    def _self_destroy(self):
        self.wp = None
        self.external_on_page_removed_asyncio_coroutine_handler = None
        self.external_on_destroy_asyncio_coroutine_handler = None
        self.app = None
        self.on_page_removed_handler_id = None
        self.destroyed = True


class OnPageDestroyClient:

    def __init__(self, wp: Optional[Union[(justpy.WebPage, Set[justpy.WebPage])]], item: Any, external_on_page_removed_coroutine_handler, external_on_destroy_coroutine_handler) -> None:
        self.wp = wp
        self.item = item
        self.item_id = id(item)
        self.external_on_page_removed_coroutine_handler = external_on_page_removed_coroutine_handler
        self.external_on_destroy_coroutine_handler = external_on_destroy_coroutine_handler
        self.linked_pages = set()
        self.app = None
        if isinstance(self.wp, justpy.WebPage):
            self.app = getattr(self.wp, 'application_instance', None)
            self.linked_pages.add(self.wp.page_id)
            self.wp.related_items[self.item_id] = self.item
        else:
            if isinstance(self.wp, set) and self.wp:
                for wp in self.wp:
                    if self.app is None:
                        self.app = getattr(wp, 'application_instance', None)
                    else:
                        if id(self.app) != id(getattr(wp, 'application_instance', None)):
                            raise DifferentApplicationsInSingleWpSetError
                        self.linked_pages.add(wp.page_id)
                        wp.related_items[self.item_id] = self.item

            else:
                pass
        self.destroyed = False

    def on_page_removed(self, i, page_id: Hashable, session_id: Hashable, user_id: Hashable):
        self.external_on_page_removed_coroutine_handler(i, page_id, session_id, user_id)
        del justpy.WebPage.instances[page_id].related_items[self.item_id]
        self.linked_pages.remove(page_id)
        if not self.linked_pages:
            self.destroy(i)

    def destroy(self, i):
        if not self.destroyed:
            for page_id in self.linked_pages:
                if self.item_id in justpy.WebPage.instances[page_id].related_items:
                    del justpy.WebPage.instances[page_id].related_items[self.item_id]

            self.external_on_destroy_coroutine_handler(i)
            self._self_destroy()

    def _self_destroy(self):
        self.wp = None
        self.item = None
        self.external_on_page_removed_coroutine_handler = None
        self.external_on_destroy_coroutine_handler = None
        self.app = None
        self.on_page_removed_handler_id = None
        self.destroyed = True


class ComponentsTreeUpdater:

    def __init__(self, *args) -> None:
        self.changes = set()
        (self.add)(*args)

    def add(self, *args):
        for item in args:
            if isinstance(item, justpy.Div):
                self._add(item)
            else:
                if isinstance(item, Node):
                    self._add(item.item)
                else:
                    if isinstance(item, Component):
                        self._add(item.html)
            try:
                for subitem in item:
                    self._add(subitem)

            except TypeError:
                pass

    def _add(self, item):
        self.changes.update((item.update for item in travers_components_tree(item)))

    def __call__(self) -> Any:

        async def coro(*args, **kwargs):
            await (asyncio.gather)(*[change(*args, **kwargs) for change in self.changes])

        return coro


class ModifyClassesMixin:

    def set_classes(self, instance: UIElement, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        raise NotImplementedError

    def sc(self, instance: UIElement, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        raise NotImplementedError

    def update_classes(self, instance: UIElement, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        raise NotImplementedError

    def uc(self, instance: UIElement, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        raise NotImplementedError


class ThemeApplierMixin(ArgsManagerMixin, ModifyClassesMixin):

    def args_manager(self, item_type: ItemType) -> ArgsManager:
        raise NotImplementedError

    def set_classes(self, instance: Container, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        raise NotImplementedError

    def update_classes(self, instance: Container, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        raise NotImplementedError

    @property
    def theme(self) -> 'ThemeArgsManager':
        raise NotImplementedError

    @property
    def translate(self) -> TextTranslationReapplier:
        raise NotImplementedError


class JpItemTranslationMixin:

    @property
    def translate(self) -> TextTranslationReapplier:
        raise NotImplementedError

    @staticmethod
    def _get_translate_me(*args, **kwargs):
        translate_me = None
        if not 1 == len(args) or kwargs:
            if not (1 == len(kwargs) and args):
                if 1 == len(kwargs):
                    translate_me = kwargs.get('translate_me', None)
                    if translate_me and not isinstance(translate_me, TranslateMe):
                        translate_me = None
                    if 1 == len(args):
                        if isinstance(args[0], TranslateMe):
                            translate_me = args[0]
            if translate_me is None:
                translate_me = TranslateMe(*args, **kwargs)
            return translate_me

    def jp_set_text(self, component: justpy.HTMLBaseComponent, *args, **kwargs):
        translate_me = (JpItemTranslationMixin._get_translate_me)(*args, **kwargs)
        jp_set_text(self.translate, translate_me.translation_id, component, translate_me.translation_template, *(translate_me.args), **translate_me.kwargs)

    def jp_set_placeholder(self, component: justpy.HTMLBaseComponent, *args, **kwargs):
        translate_me = (JpItemTranslationMixin._get_translate_me)(*args, **kwargs)
        jp_set_placeholder(self.translate, translate_me.translation_id, component, translate_me.translation_template, *(translate_me.args), **translate_me.kwargs)

    def jp_set_value(self, component: justpy.HTMLBaseComponent, *args, **kwargs):
        translate_me = (JpItemTranslationMixin._get_translate_me)(*args, **kwargs)
        jp_set_value(self.translate, translate_me.translation_id, component, translate_me.translation_template, *(translate_me.args), **translate_me.kwargs)

    def jp_set_href(self, component: justpy.HTMLBaseComponent, *args, **kwargs):
        translate_me = (JpItemTranslationMixin._get_translate_me)(*args, **kwargs)
        jp_set_href(self.translate, translate_me.translation_id, component, translate_me.translation_template, *(translate_me.args), **translate_me.kwargs)

    def jp_set_title(self, component: justpy.HTMLBaseComponent, *args, **kwargs):
        translate_me = (JpItemTranslationMixin._get_translate_me)(*args, **kwargs)
        jp_set_title(self.translate, translate_me.translation_id, component, translate_me.translation_template, *(translate_me.args), **translate_me.kwargs)


def isinstance_of_classes_list(obj: Any) -> bool:
    if isinstance(obj, list):
        return True
        return False
        return True
    return False


def isinstance_of_item_classess(obj: Any) -> bool:
    return isinstance(obj, str) or isinstance_of_classes_list(obj)


def isinstance_of_item_or_component_theme_id(obj: Any) -> bool:
    return isinstance(obj, str)


def isinstance_of_component_classes(obj: Any) -> bool:
    if isinstance(obj, dict):
        return True  # TODO: WARNING: Good enough test currently
        if len(obj) > 0:
            for another_key in obj.keys():
                key = another_key
                break
            
            if isinstance_of_item_or_component_theme_id(key):
                value = obj[key]
                if isinstance_of_component_classes(value) or isinstance_of_item_classess(value):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return True
    else:
        return False


class SubComponentTheme:

    def __init__(self, component, sub_component_id, sub_component_type, sub_component_classes):
        self.component = component
        self.component_type = type(self.component)
        self.sub_component = None
        self.sub_component_type = sub_component_type
        self.sub_component_id = sub_component_id
        self.sub_component_classes = sub_component_classes
        self.sub_component_class_modifiers = None
        self.rerun()

    def rerun(self):
        if issubclass(self.sub_component_type, Component):
            default_classes = dict()
        else:
            if issubclass(self.sub_component_type, justpy.HTMLBaseComponent) or issubclass(self.sub_component_type, justpy.WebPage):
                default_classes = str()
            else:
                raise RuntimeError(f"Wrong component type: {self.sub_component_type}")
        self.sub_component_class_modifiers = self.component.classes.get(self.sub_component_id, default_classes)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        self.sub_component = (self.sub_component_type)(*args, **kwargs)
        return self.sub_component


class TranslateMe:

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        self.translation_args = list()
        self.translation_kwargs = dict()
        self.translation_id = None
        self.translation_template = None
        self._translator = None
        self._parse()

    def _parse(self):
        args = self.args
        kwargs = self.kwargs
        first_translation_position = None
        for index, item in enumerate(args):
            if isinstance(item, TextTranslationReapplier.ToBeTranslated):
                first_translation_position = index
                break

        if first_translation_position is None:
            real_args_num = len(args)
        else:
            real_args_num = first_translation_position
        if 'translation_id' in kwargs:
            self.translation_id = kwargs['translation_id']
            del kwargs['translation_id']
        if 'translation_template' in kwargs:
            self.translation_template = kwargs['translation_template']
            del kwargs['translation_template']
        if 0 == real_args_num:
            pass
        else:
            if 1 == real_args_num:
                if self.translation_id is not None and self.translation_template is None:
                    self.translation_template = args[0]
                else:
                    if self.translation_id is None and self.translation_template is not None:
                        self.translation_id = args[0]
                    else:
                        if self.translation_id is None and self.translation_template is None:
                            self.translation_template = args[0]
                        else:
                            raise RuntimeError('There is one non-tt parameter in args, however both self.translation_id and self.translation_template were found in kwargs')
            else:
                if 2 == real_args_num:
                    if not self.translation_id is not None or self.translation_template is not None:
                        raise RuntimeError('There is two non-tt parameter in args, however one of self.translation_id or self.translation_template were found in kwargs')
                    self.translation_id = args[0]
                    self.translation_template = args[1]
                else:
                    raise RuntimeError('To many non-tt parameter in args. Must be from 0 to 2')
        if real_args_num:
            args = self.args = args[real_args_num:]

    def _translate_needed(self, text_translator: TranslationLanguageChooser, value: Any, entity_id: Optional[TextEntityId]) -> Any:
        if isinstance(value, TextTranslationReapplier.ToBeTranslated):
            return text_translator(value.text, entity_id)
        return value

    def set_translator(self, translator: Optional[Union[(TextTranslationReapplier, TranslationLanguageChooser)]]) -> 'TranslateMe':
        self._translator = translator
        return self

    def __call__(self, translator: Optional[Union[(TextTranslationReapplier, TranslationLanguageChooser)]]) -> str:
        args = self.args
        kwargs = self.kwargs
        translator = translator or self._translator
        if isinstance(translator, TextTranslationReapplier):
            translator = translator.text_translator
        if translator:
            for arg in args:
                self.translation_args.append(self._translate_needed(translator, arg, self.translation_id))

            for key, value in kwargs.items():
                self.translation_kwargs[key] = self._translate_needed(translator, value, self.translation_id)

            if self.translation_template is None:
                if self.translation_kwargs:
                    raise RuntimeError('There are tt items in kwargs, however self.translation_template was not provided or None')
                self.translated_text = ' '.join(self.translation_args)
            else:
                self.translated_text = (self.translation_template.format)(*self.translation_args, **self.translation_kwargs)
            return self.translated_text
        raise RuntimeError('No translator was provided')

    def __str__(self):
        return self.__call__()

    def __repr__(self):
        return f"<{type(self)},(translator={repr(self._translator)}, translation_id={repr(self.translation_id)}, translation_template={repr(self.translation_template)}, args={repr(self.args)}, kwargs={repr(self.kwargs)})>"


TMe = TranslateMe
__ = TranslateMe

class HashCacheContextManager:

    def __init__(self, theme_hash_cache, is_multikey, key):
        self.theme_hash_cache = theme_hash_cache
        self.is_multikey = is_multikey
        self.key = key
        self.has = None
        self.last_check_hash = None
        self.has = self.theme_hash_cache.has(self.is_multikey, self.key)
        self.last_check_hash = self.theme_hash_cache.last_check_hash

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val.with_traceback(exc_tb)

    def __bool__(self):
        return self.has

    def get(self, default: Any=None):
        return self.theme_hash_cache._get(self.last_check_hash, default)

    def set(self, value: Any):
        self.theme_hash_cache._set(self.last_check_hash, value)


class HashCacheUnsupportedDataError(Exception):
    pass


class HashCache:

    def __init__(self) -> None:
        self.data_by_hash = dict()
        self.last_check_hash = None

    def manager(self, is_multikey: bool, key: Any):
        return HashCacheContextManager(self, is_multikey, key)

    def has(self, is_multikey: bool, key: Any) -> bool:
        self.last_check_hash = self.multi_hash(key) if is_multikey else self.hash(key)
        if self.last_check_hash in self.data_by_hash:
            return True
        return False

    def get(self, is_multikey, key, default=None, use_last_check_hash=True):
        if use_last_check_hash:
            if self.last_check_hash is not None:
                return self.data_by_hash.get(self.last_check_hash, default)
        return self.data_by_hash.get(self.multi_hash(key) if is_multikey else self.hash(key), default)

    def set(self, is_multikey, key, value, use_last_check_hash=True):
        if use_last_check_hash and self.last_check_hash is not None:
            self.data_by_hash[self.last_check_hash] = value
        else:
            self.data_by_hash[self.multi_hash(key) if is_multikey else self.hash(key)] = value

    def _get(self, data_hash, default: Any=None):
        return self.data_by_hash.get(data_hash, default)

    def _set(self, data_hash, value: Any):
        self.data_by_hash[data_hash] = value

    def _immutable_single(self, data: Any) -> bool:
        return data is None or isinstance(data, int) or isinstance(data, float)

    def _immutable(self, data: Any) -> bool:
        return isinstance(data, str) or isinstance(data, tuple) or isinstance(data, frozenset) or isinstance(data, frozendict)

    def _mutable_sequence(self, data: Any) -> bool:
        return isinstance(data, list) or isinstance(data, set)

    def _mutable_map(self, data: Any) -> bool:
        return isinstance(data, dict)

    def _unknown_type_hash(self, data: Any) -> Tuple[(Hashable, int)]:
        raise HashCacheUnsupportedDataError(f"Unsupported type of key: {type(data)}; of value: {repr(data)}")

    def _hash(self, key: Any) -> Hashable:
        if self._immutable_single(key):
            return (hash(key), 1)
        if self._immutable(key):
            need_to_travers = False
            try:
                return (hash(key), len(key))
            except TypeError:
                need_to_travers = True

            if need_to_travers:
                hashes = 0
                lenghts = 0
                for item in key:
                    item_hash, item_len = self._hash(item)
                    hashes += item_hash
                    lenghts += item_len

                return (
                 hashes, lenghts)
        else:
            if self._mutable_sequence(key):
                need_to_travers = False
                try:
                    return (hash(tuple(key)), len(key))
                except TypeError:
                    need_to_travers = True

                if need_to_travers:
                    hashes = 0
                    lenghts = 0
                    for item in key:
                        item_hash, item_len = self._hash(item)
                        hashes += item_hash
                        lenghts += item_len

                    return (
                     hashes, lenghts)
            else:
                if self._mutable_map(key):
                    return self._dict_hash(key)
                return self._unknown_type_hash(key)

    def hash(self, key: Any) -> Hashable:
        item_hash, item_len = self._hash(key)
        return f"{item_hash}_{item_len}"

    def _multi_hash(self, key: Any) -> Hashable:
        result_hash = 0
        result_len = 0
        for sub_key in key:
            item_hash, item_len = self._hash(sub_key)
            result_hash += item_hash
            result_len += item_len

        return (
         result_hash, result_len)

    def multi_hash(self, key: Any) -> Hashable:
        result_hash, result_len = self._multi_hash(key)
        return f"{result_hash}_{result_len}"

    def _dict_hash(self, data: dict):
        hashes = 0
        length = 0
        for item_value in data.values():
            if self._mutable_map(item_value):
                item_hash, dict_len = self._dict_hash(item_value)
                hashes += item_hash
                length += dict_len
            else:
                item_hash, dict_len = self._hash(item_value)
                hashes += item_hash
                length += dict_len

        return (hashes, length)


class ThemeHashCache(HashCache):

    def _immutable(self, data: Any) -> bool:
        return isinstance(data, str) or isinstance(data, tuple) or isinstance(data, frozenset) or isinstance(data, frozendict)

    def _hash(self, key: Any) -> Hashable:
        if self._immutable_single(key):
            return (hash(key), 1)
        if self._immutable(key):
            return (hash(key), len(key))
        if self._mutable_sequence(key):
            return (hash(tuple(key)), len(key))
        if self._mutable_map(key):
            return self._dict_hash(key)
        return self._unknown_type_hash(key)

    def _unknown_type_hash(self, data):
        if isinstance(data, SubComponentTheme):
            data = data.sub_component_type
        if isinstance(data, type):
            type_name = str(data)
            return (
             hash(type_name), len(type_name))
        return super()._unknown_type_hash(data)


class NodeHashCache(HashCache):

    def has(self, is_multikey, key):
        if super().has(is_multikey, key):
            return True
        return False

    def _unknown_type_hash(self, data):
        if isinstance(data, SubComponentTheme):
            data = data.sub_component_type
        if isinstance(data, type):
            if issubclass(data, justpy.HTMLBaseComponent):
                type_name = str(data)
                return (
                 hash(type_name), len(type_name))
        if isinstance(data, TranslateMe):
            hashes = 0
            lenghts = 0
            for arg in data.args:
                if isinstance(arg, TextTranslationReapplier.ToBeTranslated):
                    hashes += hash(arg.text)
                    lenghts += len(arg.text)
                else:
                    data_hash, data_len = self._hash(data)
                    hashes += data_hash
                    lenghts += data_len

            data_hash, data_len = self._hash(data.kwargs)
            hashes += data_hash
            lenghts += data_len
            return (
             hashes, lenghts)
        return super()._unknown_type_hash(data)

    def _get(self, data_hash, default=None):
        return copy.copy(super()._get(data_hash, default=default))


class JpCreationTimeTranstation(ArgsManagerMixin):

    def __init__(self, translate: TextTranslationReapplier):
        self._translate = translate

    def __call__(self, entity: EntityWithExtendableArgs, *args, **kwargs) -> Tuple[(Tuple, Dict)]:
        if isinstance(entity, SubComponentTheme):
            entity = entity.sub_component_type
        if issubclass(entity, justpy.HTMLBaseComponent) or issubclass(entity, justpy.WebPage):
            new_args = list()
            for arg in args:
                if isinstance(arg, TranslateMe):
                    new_args.append(arg(self._translate))
                else:
                    new_args.append(arg)

            new_kwargs = dict()
            for key, value in kwargs.items():
                if isinstance(value, TranslateMe):
                    new_kwargs[key] = value(self._translate)
                else:
                    new_kwargs[key] = value

            return (tuple(new_args), new_kwargs)
        return (
         args, kwargs)

    def interception(self, instance: Any, entity: EntityWithExtendableArgs, original_args: Tuple[(Tuple, Dict)], resulting_args: Tuple[(Tuple, Dict)]):
        if isinstance(entity, SubComponentTheme):
            entity = entity.sub_component_type
        if issubclass(entity, justpy.HTMLBaseComponent) or issubclass(entity, justpy.WebPage):
            args, kwargs = original_args
            for key, value in kwargs.items():
                if isinstance(value, TranslateMe):
                    if 'text' == key:
                        jp_set_text(self._translate, value.translation_id, instance, value.translation_template, *(value.args), **value.kwargs)
                    else:
                        if 'placeholder' == key:
                            jp_set_placeholder(self._translate, value.translation_id, instance, value.translation_template, *(value.args), **value.kwargs)
                        else:
                            if 'value' == key:
                                jp_set_value(self._translate, value.translation_id, instance, value.translation_template, *(value.args), **value.kwargs)
                            else:
                                if 'href' == key:
                                    jp_set_href(self._translate, value.translation_id, instance, value.translation_template, *(value.args), **value.kwargs)
                    if 'title' == key:
                        jp_set_title(self._translate, value.translation_id, instance, value.translation_template, *(value.args), **value.kwargs)


class ThemeArgsManager(ArgsManagerMixin):
    hash_cache = ThemeHashCache()
    hash_cache: ThemeHashCache
    hash_cache_merge_classes = ThemeHashCache()
    hash_cache_merge_classes: ThemeHashCache
    hash_cache_modify_classes_list = ThemeHashCache()
    hash_cache_modify_classes_list: ThemeHashCache

    def __init__(self, theme: Theme):
        """[summary]

        Args:
            theme (Theme): [Original external value will not be modified inside this function]
        """
        self.history = dict()
        self.sub_items = dict()
        self.theme = None
        self.reinit_theme(theme)

    def destroy(self):
        self.history = None
        self.sub_items = None
        self.theme = None

    def __call__(self, item_type: ItemType, *args, **kwargs) -> Tuple[(Tuple, Dict)]:
        forced_theme_from = kwargs.get('forced_theme', None)
        inherit_theme_from = None
        if isinstance(item_type, SubComponentTheme):
            component_type = item_type.component_type
            sub_component_id = item_type.sub_component_id
            sub_component_type = item_type.sub_component_type
            if issubclass(sub_component_type, Component):
                subcomponent_default_classes = dict()
                inherit_theme_from = sub_component_type.inherit_theme_from
                kwargs['theme'] = self.prepare_args_manager()
            else:
                if issubclass(sub_component_type, justpy.HTMLBaseComponent) or issubclass(sub_component_type, justpy.WebPage):
                    subcomponent_default_classes = list()
            root_theme_from = forced_theme_from or inherit_theme_from or sub_component_type
            ml = self._get_component_theme_classes(root_theme_from)
            mr = self._get_component_theme_classes(component_type).get(sub_component_id, subcomponent_default_classes)
            mr1 = item_type.sub_component_classes
            mr2 = item_type.sub_component_class_modifiers
            with ThemeArgsManager.hash_cache.manager(True, (component_type, sub_component_id, ml, mr, mr1, mr2)) as cache:
                if cache:
                    kwargs['classes'] = cache.get()
                else:
                    aaa = self._merge_classes(ml, mr)
                    bbb = self._merge_classes(aaa, mr1)
                    ccc = self._merge_classes(bbb, mr2)
                    cache.set(ccc)
                    kwargs['classes'] = ccc
        else:
            if issubclass(item_type, Component):
                inherit_theme_from = item_type.inherit_theme_from
                root_theme_from = forced_theme_from or inherit_theme_from or item_type
                if 'classes' in kwargs:
                    class_modifiers = kwargs['classes']
                else:
                    class_modifiers = dict()
                kwargs['theme'] = self.prepare_args_manager()
                ctc = self._get_component_theme_classes(root_theme_from)
                with ThemeArgsManager.hash_cache.manager(True, (root_theme_from, ctc, class_modifiers)) as cache:
                    if cache:
                        kwargs['classes'] = cache.get()
                    else:
                        result_classes = self._merge_classes(ctc, class_modifiers)
                        cache.set(result_classes)
                        kwargs['classes'] = result_classes
            else:
                if issubclass(item_type, justpy.HTMLBaseComponent):
                    root_theme_from = forced_theme_from or inherit_theme_from or item_type
                    if 'classes' in kwargs:
                        class_modifiers = kwargs['classes']
                    else:
                        class_modifiers = list()
                    ctc = self._get_component_theme_classes(root_theme_from)
                    with ThemeArgsManager.hash_cache.manager(True, (root_theme_from, ctc, class_modifiers)) as cache:
                        if cache:
                            kwargs['classes'] = cache.get()
                        else:
                            result_classes = self._modify_classes_list(ctc, class_modifiers)
                            cache.set(result_classes)
                            kwargs['classes'] = result_classes
                else:
                    if issubclass(item_type, justpy.WebPage):
                        root_theme_from = forced_theme_from or inherit_theme_from or item_type
                        if 'classes' in kwargs:
                            class_modifiers = kwargs['classes']
                        if 'body_classes' in kwargs:
                            class_modifiers = kwargs['body_classes']
                        else:
                            class_modifiers = list()
                        ctc = self._get_component_theme_classes(root_theme_from)
                        with ThemeArgsManager.hash_cache.manager(True, (root_theme_from, ctc, class_modifiers)) as cache:
                            if cache:
                                kwargs['classes'] = cache.get()
                            else:
                                result_classes = ' '.join(self._modify_classes_list(ctc, class_modifiers))
                                cache.set(result_classes)
                                kwargs['body_classes'] = result_classes
                    else:
                        raise RuntimeError(f"Unsupported item_type: {type(item_type)}; of value: {item_type}")
        return (
         args, kwargs)

    def prepare_args_manager(self):
        manager = ArgsManager(self).add_interceptor(self.interception)
        return manager

    def interception(self, instance: Any, entity: EntityWithExtendableArgs, original_args: Tuple[(Tuple, Dict)], resulting_args: Tuple[(Tuple, Dict)]):
        instance_id = id(instance)
        self.history[instance_id] = (instance, entity, original_args)
        if isinstance(entity, SubComponentTheme):
            component_id = id(entity.component)
            if component_id not in self.sub_items:
                self.sub_items[component_id] = set()
            self.sub_items[component_id].add(instance_id)

    def is_in_history(self, instance_id: int):
        return instance_id in self.history

    def get_classes_history(self, instance_id: int):
        instance, entity, original_args = self.history[instance_id]
        args, kwargs = original_args
        if isinstance(entity, SubComponentTheme):
            return entity.sub_component_classes
        if issubclass(entity, Component):
            return kwargs['classes']
        if issubclass(entity, justpy.HTMLBaseComponent):
            return kwargs['classes']
        if issubclass(entity, justpy.WebPage):
            return kwargs['body_classes']
        raise RuntimeError(f"Unsupported item_type: {type(entity)}; of value: {entity}")

    def get_forced_theme(self, instance_id: int):
        instance, entity, original_args = self.history[instance_id]
        args, kwargs = original_args
        return kwargs.get('forced_theme')

    def change_classes_history(self, instance_id: int, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        instance, entity, original_args = self.history[instance_id]
        args, kwargs = original_args
        if forced_theme is not None:
            kwargs['forced_theme'] = forced_theme
        if isinstance(entity, SubComponentTheme):
            entity.sub_component_classes = classes
        else:
            if issubclass(entity, Component):
                kwargs['classes'] = classes
            else:
                if issubclass(entity, justpy.HTMLBaseComponent):
                    kwargs['classes'] = classes
                else:
                    if issubclass(entity, justpy.WebPage):
                        kwargs['body_classes'] = classes
                    else:
                        raise RuntimeError(f"Unsupported item_type: {type(entity)}; of value: {entity}")

    def repeat_instance(self, instance_id: int):
        instance, entity, original_args = self.history[instance_id]
        args, kwargs = original_args
        args, kwargs = (self.__call__)(entity, *args, **kwargs)
        if isinstance(entity, SubComponentTheme):
            entity = entity.sub_component_type
        if issubclass(entity, Component):
            instance._set_raw_classes(kwargs['classes'])
        else:
            if issubclass(entity, justpy.HTMLBaseComponent):
                instance.classes = kwargs['classes']
            else:
                if issubclass(entity, justpy.WebPage):
                    instance.body_classes = kwargs['body_classes']
                else:
                    raise RuntimeError(f"Unsupported item_type: {type(entity)}; of value: {entity}")

    def repeat_children_of(self, parent_instance_id: int):
        if parent_instance_id in self.sub_items:
            children = self.sub_items[parent_instance_id]
            for instance_id in children:
                self.repeat_instance(instance_id)

    def repeat(self):
        for instance_id in self.history.keys():
            self.repeat_instance(instance_id)

    def set_instance_classes(self, instance_id: int, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        self.change_classes_history(instance_id, classes, forced_theme)
        self.repeat_instance(instance_id)

    def update_instance_classes(self, instance_id: int, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        self.set_instance_classes(instance_id, ThemeArgsManager._modify_classes_list(self.get_classes_history(instance_id), class_modifiers), forced_theme)

    def reinit_theme(self, new_theme: Theme):
        """[summary]

        Args:
            new_theme (Theme): [Original external value will not be modified inside this function]
        """
        self.theme = ThemeArgsManager._prepare_theme(copy.deepcopy(new_theme))
        self.repeat()

    def update_theme(self, new_theme_part: Theme):
        """[summary]

        Args:
            new_theme_part (Theme): [Original external value will not be modified inside this function]
        """
        self.theme.update(ThemeArgsManager._prepare_theme(copy.deepcopy(new_theme_part)))
        self.repeat()

    @staticmethod
    def _prepare_classes_list(item_classes: ItemClasses) -> ClassesList:
        if isinstance(item_classes, str):
            item_classes = item_classes.split()
        return list(set(item_classes))

    @staticmethod
    def _prepare_theme(theme: Theme) -> Theme:
        for item_type, classes in theme.items():
            if isinstance_of_component_classes(classes):
                theme[item_type] = ThemeArgsManager._prepare_theme(classes)
            if isinstance_of_item_classess(classes):
                theme[item_type] = ThemeArgsManager._prepare_classes_list(classes)

        return theme

    def _get_component_theme_classes(self, component_type: Type) -> ComponentClasses:
        if component_type not in self.theme:
            if issubclass(component_type, Component):
                return component_type.default_theme() or dict()
            if issubclass(component_type, justpy.HTMLBaseComponent) or issubclass(component_type, justpy.WebPage):
                return list()
            return copy.copy(self.theme[component_type])

    @staticmethod
    def _modify_classes_list(theme_classes: ItemClasses, class_modifiers: ItemClasses) -> ClassesList:
        """[summary]

        Args:
            theme_classes (ItemClasses): [Original external value may be modified inside this function. Use `copy.copy(source)`, `list(source)` or `set(source)` when you need to prevent modification of the original data set]
            class_modifiers (ItemClasses): [description]

        Returns:
            ClassesList: [description]
        """
        if isinstance(theme_classes, str):
            theme_classes = theme_classes.split()
        if 1 <= len(theme_classes) and '--' == theme_classes[0]:
            theme_classes = theme_classes[1:]
            theme_classes_is_remove_all = True
        else:
            theme_classes_is_remove_all = False
        if isinstance(class_modifiers, str):
            class_modifiers = class_modifiers.split()
        if 1 <= len(class_modifiers):
            if '--' == class_modifiers[0]:
                class_modifiers = class_modifiers[1:]
                theme_classes = list()
        removed_classes = set()
        added_classes = set()
        for class_command in class_modifiers:
            if class_command.startswith('-'):
                if class_command.endswith('*'):
                    removed_class = class_command[1:-1]
                    for class_name in theme_classes:
                        if class_name.startswith(removed_class):
                            removed_class = class_name
                            break

                else:
                    removed_class = class_command[1:]
                removed_classes.add(removed_class)
            else:
                added_classes.add(class_command)

        result = remove_items_from_list(theme_classes, removed_classes, remove_duplicates=True)
        if theme_classes_is_remove_all:
            result.insert(0, '--')
        result.extend(added_classes)
        return result

    @staticmethod
    def _split_classes(classes: ItemClasses) -> ClassesList:
        """[summary]

        Args:
            classes (ItemClasses): [description]

        Raises:
            RuntimeError: [description]

        Returns:
            ClassesList: [description]
        """
        if isinstance(classes, str):
            classes = classes.split()
        if not isinstance_of_classes_list(classes):
            raise RuntimeError(f"Unsupported classes type: {type(classes)}; of value: {classes}")
        return classes

    @staticmethod
    def _merge_classes(component_classes: ComponentClasses, class_modifiers: ComponentClasses) -> ComponentClasses:
        """[Recursive]

        Args:
            component_classes (ComponentClasses): [Original external value may be modified inside this function. Use `copy.copy(source)`, `list(source)` or `set(source)` when you need to prevent modification of the original data set]
            class_modifiers (ComponentClasses): [description]

        Raises:
            RuntimeError: [description]
            RuntimeError: [description]
            RuntimeError: [description]
            RuntimeError: [description]

        Returns:
            ComponentClasses: [description]
        """
        result = None
        if isinstance_of_item_classess(component_classes):
            if not isinstance_of_item_classess(class_modifiers):
                raise RuntimeError(f"component_classes and class_modifiers type missmatch: {type(class_modifiers)}; of value: {class_modifiers}")
            component_classes = ThemeArgsManager._split_classes(component_classes)
            class_modifiers = ThemeArgsManager._split_classes(class_modifiers)
            result = ThemeArgsManager._modify_classes_list(component_classes, class_modifiers)
        else:
            if isinstance_of_component_classes(component_classes):
                for modif_key, modif_value in class_modifiers.items():
                    if modif_key not in component_classes:
                        raise RuntimeError(f"field from class_modifiers can not be found in component_classes: {type(modif_key)}; of value: {modif_key}")
                    else:
                        if modif_key not in component_classes:
                            if isinstance_of_item_classess(modif_value):
                                bare_classes = list()
                            else:
                                if isinstance_of_component_classes(modif_value):
                                    bare_classes = dict()
                                else:
                                    raise RuntimeError(f"unsupported class modifier value type: key {modif_key}; value type {type(modif_value)}; value {modif_value}")
                            component_classes[modif_key] = bare_classes
                        component_classes[modif_key] = ThemeArgsManager._merge_classes(component_classes[modif_key], modif_value)

                result = component_classes
            else:
                raise RuntimeError(f"Unsupported component_classes: {type(component_classes)}; of value: {component_classes}")
        return result

    @staticmethod
    def find(theme_applyer: Union[(ArgsManager, ThemeApplierMixin)], item_type: Optional[Union[(Type, SubComponentTheme)]]=None) -> 'ThemeArgsManager':
        if isinstance(theme_applyer, ThemeApplierMixin):
            if item_type is None:
                raise RuntimeError('item_type must be provided when the theme_applyer is a ThemeApplierMixin!')
            theme_applyer = theme_applyer.args_manager(item_type)
        for manager in theme_applyer.managers:
            if isinstance(manager, ThemeArgsManager):
                return manager

        raise RuntimeError(f"ThemeArgsManager was not found in given theme applyer of type {type(theme_applyer)}")

    def __repr__(self):
        return f"<{self.__class__.__name__}({set(self.theme) or str()})>"


def async_handle_runner(event_handler):

    async def wrapper(item, msg):
        justpy.run_task(event_handler(item, msg))

    return wrapper


def find_msg_in_args_kwargs(*args, **kwargs) -> Tuple[(bool, Any)]:
    msg = None
    if 'msg' in kwargs:
        msg = kwargs['msg']
        msg_found = True
    else:
        args_len = len(args)
        msg_found = False
        if 3 == args_len:
            msg = args[2]
            msg_found = True
        else:
            if 2 == args_len:
                msg = args[1]
                msg_found = True
    return (
     msg_found, msg)


def is_msg_processing_allowed(catch_child_events: bool, routine, *args, **kwargs) -> bool:
    msg_found, msg = find_msg_in_args_kwargs(*args, **kwargs)
    if not msg_found:
        raise RuntimeError('Could not find msg argument')
    allow_handler = False
    event_current_target = msg['event_current_target']
    form_data = msg['form_data']
    event_target = msg['event_target']
    if event_current_target:
        if event_current_target == event_target:
            allow_handler = True
        else:
            if catch_child_events:
                allow_handler = True
    else:
        if form_data:
            allow_handler = True
    return allow_handler


def event_handler(catch_child_events: bool=False):

    def real_decorator(routine):
        if inspect.iscoroutinefunction(routine):

            async def wrapper(*args, **kwargs):
                if is_msg_processing_allowed(catch_child_events, routine, *args, **kwargs):
                    await routine(*args, **kwargs)

            return wrapper

        def wrapper(*args, **kwargs):
            if is_msg_processing_allowed(catch_child_events, routine, *args, **kwargs):
                routine(*args, **kwargs)

        return wrapper

    return real_decorator


def jp_init(justpy_component_type: Type, *args, **kwargs) -> justpy.HTMLBaseComponent:
    component = justpy_component_type(*args, **kwargs)
    component.parent = None
    component.self_position_in_parent = None
    component.is_hidden = False
    for com in justpy.JustpyBaseComponent.a_add_to:
        if com in kwargs.keys():
            component.parent = kwargs[com]
            break

    return component


def jp_delete(component: justpy.HTMLBaseComponent):
    if getattr(component, 'parent', None) is not None:
        parent = component.parent
        if parent is not None:
            try:
                parent.remove_component(component)
            except Exception as ex:
                try:
                    its_ok = False
                    if len(ex.args) >= 1:
                        if 'Component cannot be removed because it is not contained in element' == ex.args[0]:
                            its_ok = True
                    if not its_ok:
                        raise
                finally:
                    ex = None
                    del ex

        parent = None
    component.delete()


def jp_hide(component: justpy.HTMLBaseComponent):
    parent = component.parent
    if parent is not None:
        position = component.parent.components.index(component)
        component.self_position_in_parent = position
        component.is_hidden = True
        parent.remove_component(component)
        return position


def jp_remove(component: justpy.HTMLBaseComponent):
    position = jp_hide(component)
    component.parent = None
    component.is_hidden = False
    return position


def jp_insert_to(component: justpy.HTMLBaseComponent, parent: Union[(justpy.HTMLBaseComponent, justpy.WebPage)], position: Optional[int]=None, slot=None):
    if isinstance(parent, justpy.HTMLBaseComponent):
        parent.add_component(component, position, slot)
    else:
        if isinstance(parent, justpy.WebPage):
            parent.add_component(component, position)
        else:
            raise RuntimeError(f"Wrong parent type: {type(parent)} of an element {repr(parent)}")
    component.parent = parent
    component.self_position_in_parent = position
    component.is_hidden = False


def jp_show(component: justpy.HTMLBaseComponent):
    jp_insert_to(component, component.parent, component.self_position_in_parent)


def jp_set_text(translate: TextTranslationReapplier, entity_id: Optional[TextEntityId], component: justpy.HTMLBaseComponent, text_template: str, *args, **kwargs):

    def set_text(text):
        component.text = text

    translate(entity_id, component, 'text', set_text, text_template, *args, **kwargs)


def jp_set_placeholder(translate: TextTranslationReapplier, entity_id: Optional[TextEntityId], component: justpy.HTMLBaseComponent, text_template: str, *args, **kwargs):

    def set_placeholder(placeholder):
        component.placeholder = placeholder

    translate(entity_id, component, 'placeholder', set_placeholder, text_template, *args, **kwargs)


def jp_set_value(translate: TextTranslationReapplier, entity_id: Optional[TextEntityId], component: justpy.HTMLBaseComponent, text_template: str, *args, **kwargs):

    def set_value(value):
        component.value = value

    translate(entity_id, component, 'value', set_value, text_template, *args, **kwargs)


def jp_set_href(translate: TextTranslationReapplier, entity_id: Optional[TextEntityId], component: justpy.HTMLBaseComponent, text_template: str, *args, **kwargs):

    def set_href(href):
        component.href = href

    translate(entity_id, component, 'href', set_href, text_template, *args, **kwargs)


def jp_set_title(translate: TextTranslationReapplier, entity_id: Optional[TextEntityId], component: JPContainer, text_template: str, *args, **kwargs):

    def set_title(title):
        component.title = title

    translate(entity_id, component, 'title', set_title, text_template, *args, **kwargs)


def jp_set_raw_classes(component: Union[(justpy.HTMLBaseComponent, justpy.WebPage)], classes: str):
    if isinstance(component, justpy.HTMLBaseComponent):
        component.classes = classes
    else:
        if isinstance(component, justpy.WebPage):
            component.body_classes = classes
        else:
            RuntimeError(f"Wrong component type: {type(component)} of an element {repr(component)}")


def jp_ensure_update_web_page(jp_web_page: justpy.WebPage) -> asyncio.Task:

    async def handler(jp_web_page: justpy.WebPage):
        await jp_web_page.update()

    return create_task(justpy.asyncio.get_event_loop(), handler, jp_web_page)


class AImpl(ThemeApplierMixin):

    def __init__(self, new_args_manager: ArgsManager, parent_container: Union[(justpy.HTMLBaseComponent, justpy.WebPage)]):
        self.new_args_manager = new_args_manager
        self.parent_container = parent_container
        self.sc = self.set_classes
        self.uc = self.update_classes

    def __call__(self, item_type: Union[(Type, SubComponentTheme)], *args, **kwargs) -> UIElement:
        return (self.args_manager(item_type))(item_type, *args, **kwargs)

    def args_manager(self, item_type: Union[(Type, SubComponentTheme)]) -> ArgsManager:
        if issubclass(item_type, Component):
            eargs = EArgs(parent=(self.parent_container))
        else:
            if issubclass(item_type, justpy.HTMLBaseComponent):
                eargs = EArgs(a=(self.parent_container))
            else:
                raise RuntimeError(f"Unsupported item_type: {type(item_type)}; of value: {item_type}")
        return self.new_args_manager.append_one_shot(eargs)

    def get_forced_theme(self, instance: UIElement) -> Optional[ItemType]:
        instance_type = type(instance)
        theme_args_manager = ThemeArgsManager.find(self.args_manager(instance_type), instance_type)
        return theme_args_manager.get_forced_theme(id(instance))

    def set_classes(self, instance: UIElement, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        instance_type = type(instance)
        theme_args_manager = ThemeArgsManager.find(self.args_manager(instance_type), instance_type)
        theme_args_manager.set_instance_classes(id(instance), classes, forced_theme)

    def update_classes(self, instance: UIElement, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        instance_type = type(instance)
        theme_args_manager = ThemeArgsManager.find(self.args_manager(instance_type), instance_type)
        theme_args_manager.update_instance_classes(id(instance), class_modifiers, forced_theme)


def _gen_a_impl(new_args_manager: ArgsManager, parent_container: Union[(justpy.HTMLBaseComponent, justpy.WebPage)]) -> ThemeApplierMixin:
    return AImpl(new_args_manager, parent_container)


class WebPageIsAlive:

    def __init__(self, wp: justpy.WebPage) -> None:
        self.wp_id = wp.page_id

    def __call__(self) -> bool:
        return self.wp_id in justpy.WebPage.instances


class Component(JpItemTranslationMixin):
    inherit_theme_from = None
    inherit_theme_from: Optional[ItemType]

    def __init__(self, *args, **kwargs):
        obj_args = tuple(merge_func_args([self._init, self.init]))
        obj_kwargs = interested_args_to_kwargs(obj_args, args, kwargs)
        parent_init_kwargs = func_args_to_kwargs(self._init, tuple(), obj_kwargs)
        child_init_kwargs = func_args_to_kwargs(self.init, tuple(), obj_kwargs)
        (self.init)(**child_init_kwargs)
        (self._init)(**parent_init_kwargs)
        self.post_construct()

    def _init(self, parent: Optional[Union[(Container, 'ParentLink')]], jp_web_page: justpy.WebPage, theme_applier: Optional['ThemeApplier']=None, ly: Optional[Union[(LoopYieldManaged, FakeLoopYieldManaged)]]=None, args_manager: Optional[ArgsManager]=None, theme: Optional[ArgsManager]=None, text_translation_reapplier: Optional[TextTranslationReapplier]=None, classes: Optional[ComponentClasses]=None, wp: Optional[Union[(justpy.WebPage, Set[justpy.WebPage])]]=None, dynamic: bool=False, dynamic_children: bool=False):
        """DO NOT FORGET TO ADD NEW PARAMETERS TO CHILD CLASSES (CoroComponent._init() for example)!!!

        Args:
            parent (Optional[Union[Container,): [description]
            jp_web_page (justpy.WebPage): [description]
            theme_applier (Optional[, optional): [description]. Defaults to None.
            ly (Optional[Union[LoopYieldManaged, FakeLoopYieldManaged]], optional): [description]. Defaults to None.
            args_manager (Optional[ArgsManager], optional): [description]. Defaults to None.
            theme (Optional[ArgsManager], optional): [description]. Defaults to None.
            text_translation_reapplier (Optional[TextTranslationReapplier], optional): [description]. Defaults to None.
            classes (Optional[ComponentClasses], optional): [description]. Defaults to None.
            wp (Optional[Union[justpy.WebPage, Set[justpy.WebPage]]], optional): [description]. Defaults to None.
            dynamic (bool, optional): [description]. Defaults to False.
            dynamic_children (bool, optional): [description]. Defaults to False.
        """
        self._deleted = False
        self.asyncio_loop = justpy.asyncio.get_event_loop()
        self.constructed = False
        self.jp_web_page = jp_web_page
        self._parent = None
        self.theme_applier = cast(ThemeApplier, theme_applier)
        self.ly = ly or gly(CoroPriority.low)
        self.args_manager = cast(ArgsManager, args_manager)
        self.wp = wp or self.jp_web_page
        self.dynamic = dynamic
        self.dynamic_children = dynamic_children
        if text_translation_reapplier is None:
            default_text_translation_reapplier = TextTranslationReapplier(TranslationLanguageChooser(TextTranslator(dict()), TranslationLanguageMapper(dict(), None)), CoroPriority.low)
            default_jp_creation_time_translation = JpCreationTimeTranstation(text_translation_reapplier)
        self._translate = cast(TextTranslationReapplier, text_translation_reapplier or default_text_translation_reapplier)
        if theme is None:
            default_theme = ThemeArgsManager(dict())
        self.theme = cast(ArgsManager, theme or ArgsManager(default_theme, default_jp_creation_time_translation))
        if theme is None:
            self.theme.add_interceptor(default_theme.interception).add_interceptor(default_jp_creation_time_translation.interception)
        self.theme_args_manager = ThemeArgsManager.find(self.theme)
        self.classes = classes or dict()
        self.stheme = self.sub_theme
        self.sth = self.stheme
        self.ssc = self.set_sub_classes
        self.usc = self.update_sub_classes
        self.tt = cast(TranslationLanguageChooser, self._translate.text_translator or TranslationLanguageChooser(TextTranslator(dict()), TranslationLanguageMapper(dict(), None)))
        if self.args_manager is None:
            self.args_manager = ArgsManager(theme or default_theme, default_jp_creation_time_translation, EArgs(text_translation_reapplier=(text_translation_reapplier or default_text_translation_reapplier)), EArgs(jp_web_page=(self.jp_web_page)))
            self.args_manager.append(EArgs(args_manager=(self.args_manager)))
            self.args_manager.add_interceptor(default_theme.interception)
            self.args_manager.add_interceptor(default_jp_creation_time_translation.interception)
        self.theme_applier = self.theme_applier or ThemeApplier(self.args_manager, self.theme, self._translate)
        self.args_manager.append(EArgs(theme_applier=theme_applier))
        self.html = None
        self.containers = {'main': None}
        self.children = list()
        if parent is not None:
            self.parent = parent
        self.on_page_destroy_client = OnPageDestroyClient(self.wp, self, self.on_page_removed, self.on_destroy)

    @property
    def translate(self) -> TextTranslationReapplier:
        return self._translate

    @translate.setter
    def translate(self, value):
        self._translate = value

    def init(self):
        """Component instance is not constructed at this point. Declare all variables needed to be in object prior self.construct() call"""
        pass

    def post_construct(self):
        pass

    @staticmethod
    def default_theme() -> Optional[ComponentClasses]:
        """should return default component's theme or None if not needed

        Returns:
            [Optional[ComponentClasses]]: [description]
        """
        pass

    @property
    def container(self) -> Optional[JPContainer]:
        return self.containers['main']

    @container.setter
    def container(self, value):
        self.containers['main'] = value

    def container_by_id(self, container_id: Optional[Hashable]=None):
        container_id = container_id or 'main'
        return self.containers[container_id]

    @property
    def parent(self) -> Optional[Container]:
        return self._parent

    @parent.setter
    def parent(self, value: Optional[Union[(Container, 'ParentLink')]]):
        if self.constructed:
            raise RuntimeError('Initiated already')
        else:
            if value is None or isinstance(value, ParentLink):
                self._parent = value
            else:
                if isinstance(value, Component) or isinstance(value, justpy.HTMLBaseComponent) or isinstance(value, justpy.WebPage):
                    self._parent = ParentLink(value)
                else:
                    raise RuntimeError(f"Wrong parent type: {type(value)}")
            if self._parent is not None:
                is_component = None
                if isinstance(self._parent.parent, Component):
                    is_component = True
                    self.container = self._parent.parent.container_by_id(self._parent.parent_container_id)
                    self._parent.parent.add_child(self)
                else:
                    if isinstance(self._parent.parent, justpy.HTMLBaseComponent) or isinstance(self._parent.parent, justpy.WebPage):
                        is_component = False
                        self.container = self._parent.parent
                    else:
                        raise RuntimeError(f"Wrong parent type: {type(value)}")
                node_was_given = False
                construct_parameters = len(inspect.signature(self.construct).parameters)
                if 0 == construct_parameters:
                    node = None
                else:
                    node = Node(self.theme_applier, self._parent, self, self.ly, self.wp, self.dynamic, False, 1)
                    node_was_given = True
                self._construct(node)
                need_to_add_to_parent = False
                if not node_was_given:
                    if isinstance(self.html, Component):
                        if not self.html.constructed:
                            need_to_add_to_parent = True
                    else:
                        need_to_add_to_parent = True
                if need_to_add_to_parent:
                    if isinstance(self._parent.parent, Component):
                        self._parent.parent.add_component(self.html)
                    else:
                        if isinstance(self.html, Component):
                            if not self.html.constructed or self.html.parent is None:
                                self.html.parent = self._parent
                        else:
                            if isinstance(self.html, justpy.HTMLBaseComponent):
                                if getattr(self.html, 'parent', None) is None:
                                    jp_insert_to(self.html, self._parent.parent)
                            else:
                                raise RuntimeError(f"Wrong component type: {type(self.html)}")

    def add_component(self, component: Container):
        return self.add_component_to('main', component)

    def add_component_to(self, contaiter_id: Hashable, component: Container):
        if contaiter_id not in self.containers:
            raise RuntimeError(f"Wrong contaiter id: {contaiter_id} for a component {type(self)}")
        container = self.containers[contaiter_id]
        if isinstance(component, Component):
            component.parent = self
            self.add_child(component)
            container.add_component(component.html)
            component.html.parent = container
        else:
            if isinstance(component, justpy.HTMLBaseComponent) or isinstance(component, justpy.WebPage):
                container.add_component(component)
                component.parent = container
            else:
                raise RuntimeError(f"Wrong component type: {type(component)}")
        return self

    def add_child(self, component: 'Component'):
        if not isinstance(component, Component):
            raise RuntimeError(f"Wrong child type: {type(component)}. Must be {type(self)}")
        self.children.append(component)

    def delete_impl(self, i):
        pass

    def _delete(self, i):
        if not self._deleted:
            self.delete_components()
            self._delete_self(i)
            self._deleted = True

    def delete(self):
        if not self._deleted:
            self.on_page_destroy_client.destroy(current_interface())

    def _delete_self(self, i):
        ly = gly(CoroPriority.low)
        self.delete_impl(i)
        ly()
        if self._is_contaiter_is_from_parent():
            del self.containers['main']
        for container_name, container in self.containers.items():
            container.delete()
            ly()

        jp_delete(self.html)
        ly()
        self.asyncio_loop = None
        self.jp_web_page = None
        self._parent = None
        self.ly = None
        self.wp = None
        self.dynamic = None
        self.dynamic_children = None
        self._translate = None
        self.theme = None
        self.theme_args_manager = None
        self.classes = None
        self.stheme = None
        self.sth = None
        self.ssc = None
        self.usc = None
        self.tt = None
        self.theme_applier = None
        self.args_manager = None
        self.html = None
        self.containers = None
        self.children = None
        self.on_page_destroy_client = None

    def destroy(self):
        return self.delete()

    def on_page_removed_impl(self, i, page_id: Hashable, session_id: Hashable, user_id: Hashable):
        pass

    def on_page_removed(self, i, page_id: Hashable, session_id: Hashable, user_id: Hashable):
        ly = gly(CoroPriority.low)
        self.on_page_removed_impl(i, page_id, session_id, user_id)
        ly()

    def on_destroy(self, i):
        self._delete(i)

    def _is_contaiter_is_from_parent(self):
        if self._parent is None:
            return False
        if isinstance(self._parent.parent, Component):
            return self.container == self._parent.parent.container
        if isinstance(self._parent.parent, justpy.HTMLBaseComponent) or isinstance(self._parent.parent, justpy.WebPage):
            return self.container == self._parent.parent
        raise RuntimeError('Unknown parent type')

    def delete_components(self):
        children_buff = self.children
        self.children = type(self.children)()
        ly = gly(CoroPriority.low)
        for child in children_buff:
            child.delete()
            ly()

    def add(self, *args):
        for component in args:
            self.add_component(component)

        return self

    def _construct(self, node: Optional['Node']):
        if node is None:
            self.construct()
        else:
            self.construct(node)
        self.constructed = True

    def construct(self, node: 'Node'):
        """There are two acceptible forms of this method: 
            1) def construct(self, node: 'Node')
            2) def construct(self)

        Args:
            node (Node): [description]

        Raises:
            NotImplementedError: [description]
        """
        raise NotImplementedError

    def hide(self):
        return jp_hide(self.html)

    def remove(self):
        return jp_remove(self.html)

    def insert_to(self, parent: justpy.HTMLBaseComponent, position: Optional[int], slot=None):
        jp_insert_to(self.html, position, slot)

    def show(self):
        return jp_show(self.html)

    def jp_ensure_update_web_page(self) -> asyncio.Task:

        async def handler(jp_web_page: justpy.WebPage):
            await jp_web_page.update()

        return create_task(self.asyncio_loop, handler, self.jp_web_page)

    def sub_theme(self, sub_component_id: Hashable, sub_component_type: Type, *args, **kwargs) -> Any:
        if issubclass(sub_component_type, Component):
            default_classes = dict()
            args_manager = self.args_manager
        else:
            if issubclass(sub_component_type, justpy.HTMLBaseComponent):
                default_classes = str()
                args_manager = self.theme
            else:
                raise RuntimeError(f"Wrong component type: {sub_component_type}")
        return args_manager(
 SubComponentTheme(self, sub_component_id, sub_component_type, kwargs.get('classes', default_classes)), *args, **kwargs)

    def set_sub_classes(self, sub_component: SubContainer, classes: ComponentClasses, forced_theme: Optional[ItemType]=None):
        self.theme_args_manager.set_instance_classes(id(sub_component), classes, forced_theme)

    def get_sub_classes_forced_theme(self, sub_component: SubContainer) -> Optional[ItemType]:
        return self.theme_args_manager.get_forced_theme(id(sub_component))

    def update_sub_classes(self, sub_component: SubContainer, class_modifiers: ItemClasses, forced_theme: Optional[ItemType]=None):
        self.theme_args_manager.update_instance_classes(id(sub_component), class_modifiers, forced_theme)

    def _set_raw_classes(self, classes):
        self.classes = classes
        self.theme_args_manager.repeat_children_of(id(self))

    def set_classes(self, classes: ComponentClasses, forced_theme: Optional[ItemType]=None):
        self.theme_args_manager.set_instance_classes(id(self), classes, forced_theme)

    def get_forced_theme(self) -> Optional[ItemType]:
        return self.theme_args_manager.get_forced_theme(id(self))

    def update_classes(self, class_modifiers: ItemClasses, forced_theme: Optional[ItemType]=None):
        self.theme_args_manager.update_instance_classes(id(self), class_modifiers, forced_theme)

    def web_page_is_alive_check(self):
        return WebPageIsAlive(self.jp_web_page)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val.with_traceback(exc_tb)

    def a(self, container_name: Hashable='main') -> ThemeApplierMixin:
        return _gen_a_impl(self.args_manager, self.containers[container_name])


class ThemeApplier(ThemeApplierMixin, JpItemTranslationMixin):

    def __init__(self, component_args_manager: ArgsManager, justpy_args_manager: ArgsManager, tanslate: TextTranslationReapplier):
        self.component_args_manager = component_args_manager
        self.justpy_args_manager = justpy_args_manager
        self.am = self.args_manager
        self._theme = ThemeArgsManager.find(self.component_args_manager)
        self._translate = tanslate
        self.sc = self.set_classes
        self.uc = self.update_classes

    def __call__(self, item_type: Union[(Type, SubComponentTheme)], *args, **kwargs) -> UIElement:
        return (self.args_manager(item_type))(item_type, *args, **kwargs)

    def args_manager(self, item_type: Union[(Type, SubComponentTheme)]) -> ArgsManager:
        entity_type = item_type
        if isinstance(item_type, SubComponentTheme):
            entity_type = item_type.sub_component_type
        if issubclass(entity_type, Component):
            return self.component_args_manager
        if issubclass(entity_type, justpy.HTMLBaseComponent) or issubclass(entity_type, justpy.WebPage):
            return self.justpy_args_manager
        raise RuntimeError(f"Wrong component type: {entity_type}")

    def set_classes(self, instance: Container, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        instance_type = type(instance)
        theme_args_manager = ThemeArgsManager.find(self.args_manager(instance_type), instance_type)
        theme_args_manager.set_instance_classes(id(instance), classes, forced_theme)

    def get_forced_theme(self, instance: Container) -> Optional[ItemType]:
        instance_type = type(instance)
        theme_args_manager = ThemeArgsManager.find(self.args_manager(instance_type), instance_type)
        return theme_args_manager.get_forced_theme(id(instance))

    def update_classes(self, instance: Container, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        instance_type = type(instance)
        theme_args_manager = ThemeArgsManager.find(self.args_manager(instance_type), instance_type)
        theme_args_manager.update_instance_classes(id(instance), class_modifiers, forced_theme)

    @property
    def theme(self) -> ThemeArgsManager:
        return self._theme

    @property
    def translate(self) -> TextTranslationReapplier:
        return self._translate


class ParentLink:

    def __init__(self, parent: Container, parent_container_id: Optional[Hashable]=None) -> None:
        self.parent = parent
        self.parent_container_id = parent_container_id


class NodeApplier(ThemeApplierMixin, JpItemTranslationMixin):
    hash_cache = NodeHashCache()
    hash_cache: NodeHashCache

    def __init__(self, node: 'Node', parent_container_id: Optional[Hashable]=None) -> None:
        self.node = node
        self.parent_container_id = parent_container_id
        self.subc = self.sub_component
        self.sc = self.set_classes
        self.uc = self.update_classes

    def __call__(self, entity: EntityWithExtendableArgs, *args, **kwargs) -> 'Node':
        own_dynamic = kwargs.get('dynamic')
        dynamic = own_dynamic if own_dynamic is not None else self.node.dynamic_children if 0 == self.node.dynamic_replica_num else self.node.dynamic
        own_dynamic_children = kwargs.get('dynamic_children')
        dynamic_children = own_dynamic_children if own_dynamic_children is not None else self.node.dynamic_children
        if 'dynamic' in kwargs:
            del kwargs['dynamic']
        if 'dynamic_children' in kwargs:
            del kwargs['dynamic_children']
        args_manager = self.node.theme_applier.args_manager(entity)
        entity_type = entity
        if isinstance(entity, SubComponentTheme):
            entity_type = entity.sub_component_type
        if issubclass(entity_type, Component):
            eargs = EArgs(wp=(self.node.wp), dynamic=dynamic, dynamic_children=dynamic_children)
        else:
            if issubclass(entity_type, justpy.HTMLBaseComponent):
                eargs = EArgs(temp=(not dynamic), id_prefix=(self.node.wp.page_id))
            else:
                raise RuntimeError(f"Unsupported item_type: {type(entity_type)}")
        args_manager.append_one_shot(eargs)
        if self.node.parent is not None:
            parent = self.node.parent.parent
            parent_container_id = self.parent_container_id or self.node.parent.parent_container_id
            parent_link = ParentLink(parent, parent_container_id)
            if issubclass(entity_type, Component):
                eargs = EArgs(parent=parent_link)
            else:
                if issubclass(entity_type, justpy.HTMLBaseComponent):
                    if isinstance(parent, Component):
                        jp_parent = parent.container_by_id(parent_container_id)
                    else:
                        jp_parent = parent
                    eargs = EArgs(a=jp_parent, parent=jp_parent, self_position_in_parent=None, is_hidden=False)
                else:
                    raise RuntimeError(f"Unsupported item_type: {type(entity_type)}")
            args_manager.append_one_shot(eargs)
        resulting_item = (self.node.theme_applier)(entity, *args, **kwargs)
        if isinstance(resulting_item, Component):
            if self.node.current_component:
                self.node.current_component.add_child(resulting_item)
            self.node.ly()
        else:
            if isinstance(resulting_item, justpy.HTMLBaseComponent):
                if not dynamic or self.node.wp is not None:
                    if isinstance(self.node.wp, justpy.WebPage):
                        resulting_item.add_page(self.node.wp)
                    else:
                        for wp in self.node.wp:
                            resulting_item.add_page(wp)

            else:
                print('Exception: Fix me: Unexpected flow: resulting_item')
                raise RuntimeError(f'Fix me: Unexpected flow: resulting_item ({repr(resulting_item)}) of type "{type(resulting_item)}"')
        return Node(self.node.theme_applier, resulting_item, self.node.current_component, self.node.ly, self.node.wp, dynamic, dynamic_children, self.node.dynamic_replica_num - 1 if 0 < self.node.dynamic_replica_num else self.node.dynamic_replica_num)

    def sub_component(self, sub_component_id: Hashable, sub_component_type: Type, *args, **kwargs) -> 'Node':
        if self.node.current_component is None:
            raise RuntimeError('current_component was not provided to Node!')
        if issubclass(sub_component_type, Component):
            default_classes = dict()
        else:
            if issubclass(sub_component_type, justpy.HTMLBaseComponent):
                default_classes = str()
            else:
                raise RuntimeError(f"Wrong component type: {sub_component_type}")
        return self(
 SubComponentTheme(self.node.current_component, sub_component_id, sub_component_type, kwargs.get('classes', default_classes)), *args, **kwargs)

    def node(self, entity: EntityWithExtendableArgs, *args, **kwargs) -> 'Node':
        """Not shure why do I need this method

        Returns:
            [type]: [description]
        """
        parent = (self.node(self.parent_container_id))(entity, *args, **kwargs)
        return Node(self, ParentLink(parent.item), self.node.current_component, self.node.ly, parent.wp, parent.dynamic, parent.dynamic_children)

    def args_manager(self, item_type: ItemType) -> ArgsManager:
        return self.node.theme_applier.args_manager(item_type)

    def set_classes(self, instance: Container, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        self.node.theme_applier.set_classes(instance, classes, forced_theme)

    def update_classes(self, instance: Container, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        self.node.theme_applier.update_classes(instance, class_modifiers, forced_theme)

    def jp_set_text(self, *args, **kwargs):
        return (super().jp_set_text)(self.node.item, *args, **kwargs)

    def jp_set_placeholder(self, *args, **kwargs):
        return (super().jp_set_placeholder)(self.node.item, *args, **kwargs)

    def jp_set_value(self, *args, **kwargs):
        return (super().jp_set_value)(self.node.item, *args, **kwargs)

    def jp_set_href(self, *args, **kwargs):
        return (super().jp_set_href)(self.node.item, *args, **kwargs)

    def jp_set_title(self, *args, **kwargs):
        return (super().jp_set_title)(self.node.item, *args, **kwargs)

    @property
    def theme(self) -> 'ThemeArgsManager':
        return self.node.theme_applier.theme

    @property
    def translate(self) -> TextTranslationReapplier:
        return self.node.theme_applier.translate

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val.with_traceback(exc_tb)


class DynamicContainerSettings:

    def __init__(self, wp: justpy.WebPage) -> None:
        pass


class Node(ThemeApplierMixin, JpItemTranslationMixin):

    def __init__(self, theme_applier: Union[(ThemeApplier, 'Node', NodeApplier)], parent: Optional[Union[(Container, ParentLink)]]=None, current_component: Optional[Component]=None, ly: Optional[Union[(LoopYieldManaged, FakeLoopYieldManaged)]]=None, wp: Optional[Union[(justpy.WebPage, Set[justpy.WebPage])]]=None, dynamic: bool=False, dynamic_children: bool=False, dynamic_replica_num: int=0) -> None:
        self._destroyed = False
        if isinstance(theme_applier, Node):
            self.theme_applier = theme_applier.theme_applier
        if isinstance(theme_applier, NodeApplier):
            self.theme_applier = theme_applier.node.theme_applier
        else:
            self.theme_applier = theme_applier
        if isinstance(parent, Component) or isinstance(parent, justpy.HTMLBaseComponent) or isinstance(parent, justpy.WebPage):
            self.parent = ParentLink(parent)
        else:
            if parent is None or isinstance(parent, ParentLink):
                self.parent = parent
            else:
                raise RuntimeError(f"Wrong theme_applier type: {type(theme_applier)}")
        self.current_component = current_component
        self.ly = ly or gly(CoroPriority.low)
        self.wp = wp
        self.dynamic = dynamic
        self.dynamic_children = dynamic_children
        self.dynamic_replica_num = dynamic_replica_num
        self.sc = self.set_classes
        self.uc = self.update_classes
        self.on_page_destroy_client = OnPageDestroyClient(self.wp, self, self.on_page_removed, self.on_destroy)

    def __call__(self, parent_container_id: Optional[Hashable]=None) -> NodeApplier:
        return NodeApplier(self, parent_container_id)

    @property
    def item(self):
        return self.parent.parent

    def node(self, entity: EntityWithExtendableArgs, *args, **kwargs) -> 'Node':
        """Not shure why do I need this method

        Returns:
            [type]: [description]
        """
        parent = (self())(entity, *args, **kwargs)
        return Node(self, ParentLink(parent.item), self.current_component, self.ly, parent.wp, parent.dynamic, parent.dynamic_children)

    def args_manager(self, item_type: ItemType) -> ArgsManager:
        return self.theme_applier.args_manager(item_type)

    def set_classes(self, instance: Container, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        self.theme_applier.set_classes(instance, classes, forced_theme)

    def update_classes(self, instance: Container, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        self.theme_applier.update_classes(instance, class_modifiers, forced_theme)

    def jp_set_text(self, *args, **kwargs):
        return (super().jp_set_text)(self.item, *args, **kwargs)

    def jp_set_placeholder(self, *args, **kwargs):
        return (super().jp_set_placeholder)(self.item, *args, **kwargs)

    def jp_set_value(self, *args, **kwargs):
        return (super().jp_set_value)(self.item, *args, **kwargs)

    def jp_set_href(self, *args, **kwargs):
        return (super().jp_set_href)(self.item, *args, **kwargs)

    def jp_set_title(self, *args, **kwargs):
        return (super().jp_set_title)(self.item, *args, **kwargs)

    @property
    def theme(self) -> 'ThemeArgsManager':
        return self.theme_applier.theme

    @property
    def translate(self) -> TextTranslationReapplier:
        return self.theme_applier.translate

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            raise exc_val.with_traceback(exc_tb)

    def on_page_removed_impl(self, i, page_id: Hashable, session_id: Hashable, user_id: Hashable):
        pass

    def on_page_removed(self, i, page_id: Hashable, session_id: Hashable, user_id: Hashable):
        ly = gly(CoroPriority.low)
        self.on_page_removed_impl(i, page_id, session_id, user_id)
        ly()

    def destroy_impl(self, i):
        pass

    def _self_destroy(self, i):
        ly = gly(CoroPriority.low)
        self.destroy_impl(i)
        ly()
        self.theme_applier = None
        self.parent = None
        self.current_component = None
        self.ly = None
        self.wp = None
        self.dynamic = None
        self.dynamic_children = None
        self.dynamic_replica_num = None
        self.sc = None
        self.uc = None
        self.on_page_destroy_client = None

    def _destroy(self, i):
        if not self._destroyed:
            if self.current_component is not None:
                if isinstance(self.current_component, Component):
                    self.current_component.destroy()
            self._self_destroy(i)
            self._destroyed = True

    def destroy(self):
        if not self._destroyed:
            self.on_page_destroy_client.destroy(current_interface())

    def on_destroy(self, i):
        self._destroy(i)


class INodeImpl(ModifyClassesMixin):

    def __init__(self, item: Container, new_args_manager: ArgsManager):
        self._item = item
        self._new_args_manager = new_args_manager
        self.sc = self.set_classes
        self.uc = self.update_classes

    def __call__(self, container_name: Hashable='main') -> ThemeApplierMixin:
        if isinstance(self._item, Component):
            parent_container = self._item.containers[container_name]
        else:
            if isinstance(self._item, justpy.HTMLBaseComponent) or isinstance(self._item, justpy.WebPage):
                parent_container = self._item
            else:
                raise RuntimeError(f"Unsupported item with type: {type(self._item)}")
        return _gen_a_impl(self._new_args_manager, parent_container)

    @property
    def item(self) -> Container:
        return self._item

    def set_classes(self, instance: UIElement, classes: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        theme_args_manager = ThemeArgsManager.find(self._new_args_manager, type(instance))
        theme_args_manager.set_instance_classes(id(instance), classes, forced_theme)

    def get_forced_theme(self, instance: UIElement) -> Optional[ItemType]:
        theme_args_manager = ThemeArgsManager.find(self._new_args_manager, type(instance))
        return theme_args_manager.get_forced_theme(id(instance))

    def update_classes(self, instance: UIElement, class_modifiers: Union[(ItemClasses, ComponentClasses)], forced_theme: Optional[ItemType]=None):
        theme_args_manager = ThemeArgsManager.find(self._new_args_manager, type(instance))
        theme_args_manager.update_instance_classes(id(instance), class_modifiers, forced_theme)


def _get_inode_impl(item: Container, theme_applyer: Optional[Union[(ArgsManager, ThemeApplierMixin)]]=None) -> INodeImpl:
    if isinstance(item, Component):
        new_args_manager = item.args_manager
    else:
        if isinstance(item, justpy.HTMLBaseComponent) or isinstance(item, justpy.WebPage):
            if not theme_applyer:
                raise RuntimeError(f"theme_applyer must be set for the item of type: {type(item)}")
            if isinstance(theme_applyer, ArgsManager):
                new_args_manager = theme_applyer
            else:
                if isinstance(theme_applyer, ThemeApplierMixin):
                    new_args_manager = theme_applyer.args_manager(type(item))
        else:
            raise RuntimeError(f"Unsupported item with type: {type(item)}")
    return INodeImpl(item, new_args_manager)


@contextmanager
def inode(item: Container, theme_applyer: Optional[Union[(ArgsManager, ThemeApplierMixin)]]=None):
    """Item node. Good for a fast prototyping

    Args:
        item (Container): [description]
        theme_applyer (Optional[Union[ArgsManager, ThemeApplierMixin]], optional): [description]. Defaults to None.

    Yields:
        INodeImpl: [description]
    """
    yield _get_inode_impl(item, theme_applyer)


@contextmanager
def tnode(theme_applyer: Union[(ArgsManager, ThemeApplierMixin)], item_type: Type, *args, **kwargs):
    """Type node. Good for a fast prototyping

    Args:
        theme_applyer (Union[ArgsManager, ThemeApplierMixin]): [description]
        item_type (Type): [description]

    Yields:
        INodeImpl: [description]
    """
    item = theme_applyer(item_type, *args, **kwargs)
    yield _get_inode_impl(item, theme_applyer)


def delete_component(component: Container):
    if isinstance(component, Component):
        component.delete()
    else:
        if isinstance(component, justpy.HTMLBaseComponent):
            jp_delete(component)
        else:
            raise RuntimeError(f"Wrong component type: {type(component)}")


def hide_component(component: Container):
    if isinstance(component, Component):
        component.hide()
    else:
        if isinstance(component, justpy.HTMLBaseComponent):
            jp_hide(component)
        else:
            raise RuntimeError(f"Wrong component type: {type(component)}")


def remove_component(component: Container):
    if isinstance(component, Component):
        component.remove()
    else:
        if isinstance(component, justpy.HTMLBaseComponent):
            jp_remove(component)
        else:
            raise RuntimeError(f"Wrong component type: {type(component)}")


def insert_component_to(component: Container, parent: justpy.HTMLBaseComponent, position: Optional[int], slot=None):
    if isinstance(component, Component):
        component.insert_to(parent, position, slot)
    else:
        if isinstance(component, justpy.HTMLBaseComponent):
            jp_insert_to(component, parent, position, slot)
        else:
            raise RuntimeError(f"Wrong component type: {type(component)}")


def show_component(component: Container):
    if isinstance(component, Component):
        component.show()
    else:
        if isinstance(component, justpy.HTMLBaseComponent):
            jp_show(component)
        else:
            raise RuntimeError(f"Wrong component type: {type(component)}")


def jp_set_classes(theme_args_manager: ThemeArgsManager, item: Union[(justpy.HTMLBaseComponent, justpy.WebPage)], classes: ItemClasses, forced_theme: Optional[ItemType]=None):
    item_id = id(item)
    theme_args_manager.change_classes_history(item_id, classes, forced_theme)
    theme_args_manager.repeat_instance(item_id)


def get_theme_from_applyer(theme_applyer: Union[(ArgsManager, ThemeApplierMixin)], component_type: Type) -> ThemeArgsManager:
    if isinstance(theme_applyer, ArgsManager):
        args_manager = theme_applyer
    else:
        if isinstance(theme_applyer, ThemeApplierMixin):
            args_manager = theme_applyer.args_manager(component_type)
        else:
            raise RuntimeError(f"Wrong theme_applyer type: {type(theme_applyer)}")
    theme_args_manager = ThemeArgsManager.find(theme_applyer)


def set_classes(theme_applyer: Union[(ArgsManager, ThemeApplierMixin)], component: Container, classes: ComponentClasses, forced_theme: Optional[ItemType]=None):
    theme_args_manager = ThemeArgsManager.find(theme_applyer, type(component))
    theme_args_manager.set_instance_classes(id(component), classes, forced_theme)


sc = set_classes

def get_forced_theme(theme_applyer: Union[(ArgsManager, ThemeApplierMixin)], component: Container) -> Optional[ItemType]:
    theme_args_manager = ThemeArgsManager.find(theme_applyer, type(component))
    return theme_args_manager.get_forced_theme(id(component))


gft = get_forced_theme

def update_classes(theme_applyer: Union[(ArgsManager, ThemeApplierMixin)], component: Container, class_modifiers: ItemClasses, forced_theme: Optional[ItemType]=None):
    theme_args_manager = ThemeArgsManager.find(theme_applyer, type(component))
    theme_args_manager.update_instance_classes(id(component), class_modifiers, forced_theme)


uc = update_classes

@contextmanager
def parent(item):
    if isinstance(item, Component):
        yield item.parent
    else:
        if isinstance(item, justpy.HTMLBaseComponent):
            if hasattr(item, 'a'):
                yield item.a
            else:
                yield
        else:
            raise RuntimeError(f"Wrong component type: {type(item)}")


def jp_entity_from_parent_link(parent_link: ParentLink) -> JPContainer:
    jp_entity = None
    if parent_link is not None:
        parent = parent_link.parent
        parent_container_id = parent_link.parent_container_id
        if isinstance(parent, Component):
            jp_entity = parent.container_by_id(parent_container_id)
        else:
            jp_entity = parent
    return jp_entity