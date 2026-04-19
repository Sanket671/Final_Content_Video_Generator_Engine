from pytrends.request import TrendReq
from pytrends import exceptions


def get_trending_keywords():

    fallback_keywords = [
        "athlete training",
        "sports recovery",
        "sports technology",
        "injury prevention",
        "sports performance"
    ]

    try:
        pytrends = TrendReq(hl="en-US", tz=330)

        pytrends.build_payload(fallback_keywords, timeframe="now 7-d")

        related = pytrends.related_queries()

        results = []

        for key in related:
            top_df = related[key].get("top")
            if top_df is not None:
                for query in top_df["query"].head(5):
                    results.append(query)

        results = list(dict.fromkeys(results))  # preserve order and de-dupe
        return results[:15] if results else fallback_keywords

    except exceptions.TooManyRequestsError:
        print("Warning: Too many requests to Google Trends (429). Using fallback keywords.")
        return fallback_keywords
    except Exception as err:
        print(f"Warning: Could not fetch trending keywords ({err}). Using fallback keywords.")
        return fallback_keywords