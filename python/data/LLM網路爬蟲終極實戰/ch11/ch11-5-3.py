import asyncio
import json
from crawl4ai import JsonCssExtractionStrategy, LLMConfig

sample_html = """
<div class="product">
   <h2>HP 筆記型電腦</h2>
   <span class="price">$999.99</span>
     <div class="rating" data-score="4.5">★★★★☆</div>
</div>
"""

def auto_generate_schema():    
    try:
        schema = JsonCssExtractionStrategy.generate_schema(
            sample_html,
            llm_config=LLMConfig(
                provider="ollama/llama3.1:8b",
                api_token=None
            )
        )
        print("LLM自動生成的擷取結構:")
        print(json.dumps(schema, indent=2, ensure_ascii=False))
    except Exception as e:
        print("需要Ollama:", e)

auto_generate_schema()