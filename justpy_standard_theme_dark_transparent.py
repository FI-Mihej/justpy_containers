__all__ = [
 'theme']
from low_latency_justpy import justpy as jp, init_scheduler
from justpy_components import *
from justpy_coro_helpers import *
from justpy_standard_components import *
theme: Theme = {jp.Button: 'select-none h-auto m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 text-black rounded hover:bg-yellow-400 active:bg-yellow-300', 
 jp.Label: 'bg-gray-200 text-gray-600 font-semibold py-1 px-2 border border-gray-400 rounded-r shadow', 
 jp.Input: 'shadow appearance-none border rounded-l w-full py-2 px-3 text-gray-700 border-gray-700 leading-tight focus:outline-none focus:shadow-outline h-auto', 
 jp.Textarea: 'bg-opacity-50 bg-gray-800 text-gray-400 placeholder-gray-600 appearance-none border border-gray-800 rounded shadow w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline h-auto', 
 jp.EditorMD: 'bg-opacity-50 bg-gray-600 text-gray-300', 
 jp.Markdown: 'bg-opacity-50 rounded bg-white p-5', 
 jp.PlotlyChart: 'bg-opacity-50 rounded bg-white p-5', 
 jp.P: 'text-gray-500 text-xs break-words', 
 jp.H1: 'select-none font-medium font-sans text-6xl subpixel-antialiased not-italic text-yellow-500', 
 jp.H2: 'select-none font-medium font-sans text-5xl subpixel-antialiased not-italic text-yellow-500', 
 jp.H3: 'select-none font-medium font-sans text-4xl subpixel-antialiased not-italic text-yellow-500', 
 jp.H4: 'select-none font-medium font-sans text-3xl subpixel-antialiased not-italic text-yellow-500', 
 jp.H5: 'select-none font-medium font-sans text-2xl subpixel-antialiased not-italic text-yellow-500', 
 jp.H6: 'select-none font-medium font-sans text-xl subpixel-antialiased not-italic text-yellow-500', 
 jp.Hr: 'mt-1 mb-2', 
 WindowTitleTextForApp: 'select-none font-light font-sans text-sm subpixel-antialiased not-italic text-gray-500', 
 jp.A: 'text-xs text-blue-300 hover:underline visited:text-purple-300', 
 Screen: {'screen': 'bg-gray-900'}, 
 
 ScreenWithHeaderAndFooter: {'screen': 'bg-gray-900'}, 
 
 ScreenWithStickyHeaderAndFooter: {'screen': 'bg-opacity-75 bg-gray-900'}, 
 
 AnAppScreenWithStickyHeaderAndFooter: {'screen': {'screen': 'bg-opacity-75 bg-gray-900'}}, 
 
 Pannels: {'pan_l_classes':'p-5', 
           'pan_r_classes':'p-5'}, 
 
 LanguageSelector: {'selector':'h-auto text-xs m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 rounded hover:bg-yellow-400', 
                    'selector_language':'bg-gray-800 text-gray-400 text-xs'}, 
 
 ThemeSelector: {
                  'html': 'text-sm',
                  'selector': 'h-auto text-xs m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 disabled:bg-yellow-900 rounded hover:bg-yellow-400',
                  'dilabled_selector': 'h-auto text-xs m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 disabled:bg-yellow-900 rounded',
                  'selector_language': 'bg-gray-800 text-gray-400 text-xs'}, 
 
 ThemeSelectorForApp: {'selector':'h-auto text-xs m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 disabled:bg-yellow-900 rounded hover:bg-yellow-400', 
                       'dilabled_selector':'h-auto text-xs m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 disabled:bg-yellow-900 rounded', 
                       'selector_language':'bg-gray-800 text-gray-400 text-xs'}, 
 
 Main: {'html_container': ''}, 
 
 Header: {'html':'bg-gray-800 p-2', 
          'lang_select':{}}, 
 
 HeaderForApp: {'html':'bg-opacity-50 bg-gray-800', 
                'lang_select':{}}, 
 
 Footer: {'html': 'bg-gray-800 p-2'}, 
 
 FooterCendered: {'html': 'bg-gray-800 p-2'}, 
 
 FooterWithLangSelect: {'html':'bg-gray-800 p-2', 
                        'lang_select':{}}, 
 
 FooterWithLangSelectLayered: {'html':'bg-gray-800 p-2', 
                               'lang_select':{}}, 
 
 FooterWithLangSelectForApp: {'html':'bg-opacity-50 bg-gray-800 p-2', 
                              'lang_select':{}}, 
 
 FooterWithLangSelectLayeredForApp: {'html':'bg-opacity-0 bg-gray-800 p-2', 
                                     'lang_select':{}}, 
 
 FooterContentSimple: {'html': '-text-xs font-light font-sans text-base subpixel-antialiased not-italic'}, 
 
 InitialRequestView: {'html': ''}, 
 
 RegisterForm: {'background':{'screen': 'opacity-75'}, 
                'form':'m-5 p-3 bg-gray-900 border border-gray-400 rounded-md', 
                'form_close_button':'text-gray-500 hover:text-gray-100 hover:bg-red-400 rounded', 
                'form_head':'bg-gray-900 text-yellow-500', 
                'user_name_label':'text-gray-400 text-xs font-bold', 
                'user_name_input':'', 
                'user_email_label':'text-gray-400 text-xs font-bold', 
                'user_email_input':'', 
                'user_password_label':'text-gray-400 text-xs font-bold', 
                'user_password_input':'', 
                'send_stuff_label':'text-sm text-gray-700', 
                'send_stuff_checkbox':'text-blue-500', 
                'form_submit_button':''}, 
 
 LoginForm: {'background':{'screen': 'opacity-75'}, 
             'form':'m-5 p-3 bg-gray-900 border border-gray-400 rounded-md', 
             'form_close_button':'text-gray-500 hover:text-gray-100 hover:bg-red-400 rounded', 
             'form_head':'bg-gray-900 text-yellow-500', 
             'user_name_label':'text-gray-400 text-xs font-bold', 
             'user_name_input':'', 
             'user_password_label':'text-gray-400 text-xs font-bold', 
             'user_password_input':'', 
             'send_stuff_label':'text-sm text-gray-700', 
             'send_stuff_checkbox':'text-blue-500', 
             'form_submit_button':''}, 
 
 LoginFormForApp: {'background':{'screen': 'opacity-0'}, 
                   'frontend':{},  'form':'m-5 p-3 bg-gray-900 border border-gray-400 rounded-md', 
                   'form_close_button':'text-gray-500 hover:text-gray-100 hover:bg-red-400 rounded', 
                   'form_head':'bg-gray-900 text-yellow-500', 
                   'user_name_label':'text-gray-400 text-xs font-bold', 
                   'user_name_input':'', 
                   'user_password_label':'text-gray-400 text-xs font-bold', 
                   'user_password_input':'', 
                   'send_stuff_label':'text-sm text-gray-700', 
                   'send_stuff_checkbox':'text-blue-500', 
                   'form_submit_button':''}, 
 
 Tooltip: {'container':'', 
           'container_with_text':'bg-opacity-80 bg-gray-700 text-gray-400 text-center rounded-lg pt-2 pr-5 pl-5 pb-1'}}