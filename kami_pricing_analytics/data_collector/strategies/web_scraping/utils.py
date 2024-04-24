import itertools
from collections import defaultdict

import requests


def jaccard_similarity(content1, content2):
    """Calculate the Jaccard Similarity between two strings."""
    set1 = set(content1.split())
    set2 = set(content2.split())
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    return len(intersection) / len(union) if union else 0


def group_user_agents_by_content_similarity(user_agents, url, threshold=0.8):
    """
    Makes HTTP requests to the given URL with different user agents and groups them
    based on the similarity of the HTML content returned.

    Args:
        user_agents (list): A list of user agent strings to test.
        url (str): The target URL from which to fetch content.
        threshold (float): The similarity threshold to consider two contents as similar.

    Returns:
        list: A list of lists, where each sublist contains user agents that received
        similar HTML content based on the defined threshold.
    """
    responses = {}

    # Fetch the HTML content for each user agent and store it
    for ua in user_agents:
        headers = {'User-Agent': ua}
        response = requests.get(url, headers=headers)
        content = response.text.strip()
        responses[ua] = content

    # Calculate similarity between all pairs of content
    compared = set()
    groups = []
    for ua1, ua2 in itertools.combinations(responses.keys(), 2):
        pair = frozenset([ua1, ua2])
        if pair not in compared:
            compared.add(pair)
            if jaccard_similarity(responses[ua1], responses[ua2]) >= threshold:
                # Merge groups containing ua1 or ua2
                merged_group = {ua1, ua2}
                groups_to_merge = []
                for group in groups:
                    if ua1 in group or ua2 in group:
                        merged_group.update(group)
                        groups_to_merge.append(group)
                for group in groups_to_merge:
                    groups.remove(group)
                groups.append(merged_group)

    # Add any user agents that have not been grouped
    all_grouped_ua = set(itertools.chain.from_iterable(groups))
    for ua in responses.keys():
        if ua not in all_grouped_ua:
            groups.append({ua})

    return [list(group) for group in groups]


def group_user_agents_by_identical_content(user_agents, url):
    """
    Makes HTTP requests to the given URL with different user agents and groups them
    based on the similarity of the HTML content returned.

    Args:
        user_agents (list): A list of user agent strings to test.
        url (str): The target URL from which to fetch content.

    Returns:
        list: A list of lists, where each sublist contains user agents that received
        the same HTML content.
    """
    # Dictionary to store responses with HTML content as key and list of user agents as value
    content_dict = defaultdict(list)

    # Fetch the HTML content for each user agent
    for ua in user_agents:
        headers = {'User-Agent': ua}
        response = requests.get(url, headers=headers)
        content = response.text

        # Normalize content for comparison (optional, could be more sophisticated)
        normalized_content = content.strip()

        # Group user agents by identical HTML content
        content_dict[normalized_content].append(ua)

    # Only return groups of user agents
    return list(content_dict.values())
