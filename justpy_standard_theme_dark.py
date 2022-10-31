__all__ = [
 'theme']
from low_latency_justpy import justpy as jp, init_scheduler
from justpy_components import *
from justpy_coro_helpers import *
from justpy_standard_components import *
theme: Theme = {jp.WebPage: 'bg-gray-900', 
 WebPageForApp: 'bg-gray-900 bg-opacity-50', 
 jp.Button: 'select-none w-48 h-auto text-base m-2 p-1 bg-yellow-500 text-black rounded hover:bg-yellow-400 active:bg-yellow-300', 
 jp.Label: 'bg-gray-200 text-gray-800 font-semibold py-1 px-2 border border-gray-400 rounded-r shadow', 
 jp.Input: 'shadow appearance-none border rounded-l w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline h-auto', 
 jp.Textarea: 'bg-opacity-50 bg-gray-600 text-gray-300 shadow appearance-none border rounded-l w-full py-2 px-3 leading-tight focus:outline-none focus:shadow-outline h-auto', 
 jp.EditorMD: 'bg-opacity-50 bg-gray-600 text-gray-300', 
 jp.Markdown: 'rounded bg-white bg-opacity-50 p-5', 
 jp.PlotlyChart: 'rounded bg-white bg-opacity-25 p-5', 
 jp.P: 'text-gray-400 text-xs break-words', 
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
 
 Pannels: {'pan_l_classes':'p-5', 
           'pan_r_classes':'p-5'}, 
 
 LanguageSelector: {'selector':'w-16 h-auto text-xs m-2 p-1 bg-yellow-500 rounded hover:bg-yellow-400', 
                    'selector_language':'bg-gray-800 text-gray-400 text-xs'}, 
 
 Main: {'html_container': ''}, 
 
 Header: {'html':'bg-gray-800 p-2', 
          'lang_select':{}}, 
 
 HeaderForApp: {'html':'bg-gray-800 bg-opacity-50', 
                'lang_select':{}}, 
 
 Footer: {'html': 'bg-gray-800 p-2'}, 
 
 FooterCendered: {'html': 'bg-gray-800 p-2'}, 
 
 FooterWithLangSelect: {'html':'bg-gray-800 p-2', 
                        'lang_select':{}}, 
 
 FooterWithLangSelectForApp: {'html':'bg-gray-800 p-2 bg-opacity-50', 
                              'lang_select':{}}, 
 
 FooterContentSimple: {'html': '-text-xs font-light font-sans text-base subpixel-antialiased not-italic'}, 
 
 InitialRequestView: {'html': ''}, 
 
 LoginForm: {'background': {'screen': ''}}}