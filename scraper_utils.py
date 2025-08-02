
import requests
from bs4 import BeautifulSoup
# import re

# LeetCode - Using GraphQL API

def fetch_leetcode_stats(username):
    try:
        url = "https://leetcode.com/graphql"
        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/{username}/",
            "User-Agent": "Mozilla/5.0"
        }

        query = {
            "query": """
            query userProblemsSolved($username: String!) {
                allQuestionsCount {
                    difficulty
                    count
                }
                matchedUser(username: $username) {
                    problemsSolvedBeatsStats {
                        difficulty
                        percentage
                    }
                    submitStatsGlobal {
                        acSubmissionNum {
                            difficulty
                            count
                        }
                    }
                }
            }
            """,
            "variables": {"username": username}
        }

        response = requests.post(url, json=query, headers=headers)
        if response.status_code != 200:
            return {'error': f'Unable to fetch LeetCode profile (HTTP {response.status_code})'}

        data = response.json()
        user_data = data['data'].get('matchedUser')
        if not user_data:
            return {'error': 'LeetCode user not found or profile is private'}

        submissions = user_data['submitStatsGlobal']['acSubmissionNum']
        result = {}
        for item in submissions:
            difficulty = item['difficulty'].lower()
            result[f"{difficulty}Solved"] = item['count']
        result['totalSolved'] = sum(item['count'] for item in submissions if item['difficulty'] != 'All')

        return result
    except Exception as e:
        print(f"LeetCode fetch error: {e}")
        return {'error': f'Exception occurred: {e}'}


# GeeksforGeeks

def fetch_gfg_stats(username):
    try:
        url = f"https://geeks-for-geeks-api.vercel.app/{username}"
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            return {'error': f'GFG profile not found (HTTP {response.status_code})'}
        data = response.json()
        info = data.get('info', {})
        solved = data.get('solvedStats', {})

        return {
            'coding_score': info.get('codingScore', 'N/A'),
            'total_solved': info.get('totalProblemsSolved', 'N/A'),
            'easy_solved': solved.get('easy', {}).get('count', 'N/A'),
            'medium_solved': solved.get('medium', {}).get('count', 'N/A'),
            'hard_solved': solved.get('hard', {}).get('count', 'N/A')
        }
    except Exception as e:
        print(f"GFG fetch error: {e}")
        return {'error': f'Exception occurred: {e}'}

