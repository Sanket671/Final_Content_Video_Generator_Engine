import sys
sys.path.append('d:/6th Sem Engineering/final_EDAI/Video_Generation_Engine')
from renderer import stock_broll_manager
from planner.visual_mapper import resolve_visual

print('get_stock_broll callable:', hasattr(stock_broll_manager, 'get_stock_broll'))
print('sample get_stock_broll("star") ->', stock_broll_manager.get_stock_broll('star'))
print('visual for review_text overlay ->', resolve_visual({'scene_type':'review_text','overlay':'⭐ 4.6+ Rated'}, [], 0))
