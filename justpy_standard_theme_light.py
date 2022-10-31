__all__ = [
 'theme']
from low_latency_justpy import justpy as jp, init_scheduler
from justpy_components import *
from justpy_coro_helpers import *
from justpy_standard_components import *
theme: Theme = {jp.WebPage: 'bg-gray-100', 
 WebPageForApp: 'bg-gray-100', 
 jp.Button: 'select-none h-auto m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 text-black rounded hover:bg-yellow-600 active:bg-yellow-700', 
 jp.Label: 'bg-gray-200 text-gray-800 font-semibold py-1 px-2 border border-gray-400 rounded-r shadow', 
 jp.Input: 'shadow appearance-none border rounded-l w-full py-2 px-3 text-gray-700 border-gray-300 leading-tight focus:outline-none focus:shadow-outline h-auto', 
 jp.Textarea: 'bg-gray-200 text-gray-500 placeholder-gray-400 appearance-none border rounded shadow w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline h-auto', 
 jp.EditorMD: 'bg-gray-400 text-gray-700', 
 jp.Markdown: 'rounded bg-white p-5', 
 jp.PlotlyChart: 'rounded bg-white p-5', 
 jp.P: 'text-gray-500 text-xs break-words', 
 jp.H1: 'select-none font-medium font-sans text-6xl subpixel-antialiased not-italic text-yellow-600', 
 jp.H2: 'select-none font-medium font-sans text-5xl subpixel-antialiased not-italic text-yellow-600', 
 jp.H3: 'select-none font-medium font-sans text-4xl subpixel-antialiased not-italic text-yellow-600', 
 jp.H4: 'select-none font-medium font-sans text-3xl subpixel-antialiased not-italic text-yellow-600', 
 jp.H5: 'select-none font-medium font-sans text-2xl subpixel-antialiased not-italic text-yellow-600', 
 jp.H6: 'select-none font-medium font-sans text-xl subpixel-antialiased not-italic text-yellow-600', 
 jp.Hr: 'mt-1 mb-2', 
 WindowTitleTextForApp: 'select-none font-light font-sans text-sm subpixel-antialiased not-italic text-gray-500', 
 jp.A: 'text-xs text-blue-300 hover:underline visited:text-purple-300', 
 Screen: {'screen': 'bg-gray-100'}, 
 
 ScreenWithHeaderAndFooter: {'screen': 'bg-gray-100'}, 
 
 Pannels: {'pan_l_classes':'p-5', 
           'pan_r_classes':'p-5'}, 
 
 LanguageSelector: {'selector':'h-auto text-xs m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 rounded hover:bg-yellow-600', 
                    'selector_language':'bg-gray-200 text-gray-600 text-xs'}, 
 
 ThemeSelector: {
                  'html': 'text-sm',
                  'selector': 'h-auto text-xs m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 disabled:bg-yellow-100 rounded hover:bg-yellow-600',
                  'dilabled_selector': 'h-auto text-xs m-2 pt-1 pb-1 pl-3 pr-3 bg-yellow-500 disabled:bg-yellow-100 rounded',
                  'selector_language': 'bg-gray-200 text-gray-600 text-xs'}, 
 
 Main: {'html_container': ''}, 
 
 Header: {'html':'bg-gray-200 p-2', 
          'lang_select':{}}, 
 
 HeaderForApp: {'html':'bg-gray-200', 
                'lang_select':{}}, 
 
 Footer: {'html': 'bg-gray-200 p-2'}, 
 
 FooterCendered: {'html': 'bg-gray-200 p-2'}, 
 
 FooterWithLangSelect: {'html':'bg-gray-200 p-2', 
                        'lang_select':{}}, 
 
 FooterWithLangSelectLayered: {'html':'bg-gray-200 p-2', 
                               'lang_select':{}}, 
 
 FooterWithLangSelectForApp: {'html':'bg-gray-200 p-2', 
                              'lang_select':{}}, 
 
 FooterContentSimple: {'html': '-text-xs font-light font-sans text-base subpixel-antialiased not-italic'}, 
 
 InitialRequestView: {'html': ''}, 
 
 RegisterForm: {'background':{'screen': 'opacity-75'}, 
                'form':'m-5 p-3 bg-gray-100 border border-gray-600 rounded-md', 
                'form_close_button':'text-gray-500 hover:text-gray-900 hover:bg-red-600 rounded', 
                'form_head':'bg-gray-100 text-yellow-500', 
                'user_name_label':'text-gray-600 text-xs font-bold', 
                'user_name_input':'', 
                'user_email_label':'text-gray-600 text-xs font-bold', 
                'user_email_input':'', 
                'user_password_label':'text-gray-600 text-xs font-bold', 
                'user_password_input':'', 
                'send_stuff_label':'text-sm text-gray-300', 
                'send_stuff_checkbox':'text-blue-500', 
                'form_submit_button':''}, 
 
 LoginForm: {'background':{'screen': 'opacity-75'}, 
             'form':'m-5 p-3 bg-gray-100 border border-gray-600 rounded-md', 
             'form_close_button':'text-gray-500 hover:text-gray-900 hover:bg-red-600 rounded', 
             'form_head':'bg-gray-100 text-yellow-500', 
             'user_name_label':'text-gray-600 text-xs font-bold', 
             'user_name_input':'', 
             'user_password_label':'text-gray-600 text-xs font-bold', 
             'user_password_input':'', 
             'send_stuff_label':'text-sm text-gray-300', 
             'send_stuff_checkbox':'text-blue-500', 
             'form_submit_button':''}, 
 
 Tooltip: {'container':'', 
           'container_with_text':'bg-opacity-80 bg-gray-300 text-gray-600 text-center rounded-lg pt-2 pr-5 pl-5 pb-1'}}