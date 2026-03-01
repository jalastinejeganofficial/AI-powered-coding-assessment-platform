from sqlalchemy.orm import Session
from models.dsa_questions import DSAQuestion, DifficultyLevel
from utils.database_utils import get_dsa_questions_by_difficulty


def load_sample_questions(db: Session):
    """Load sample DSA questions into the database"""
    
    sample_questions = [
        # Beginner Questions
        {
            "title": "Two Sum",
            "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.",
            "difficulty": DifficultyLevel.BEGINNER,
            "category": "algorithms",
            "solution": "Use a hash map to store values and their indices. For each element, check if (target - current_element) exists in the hash map.",
            "hints": "1. Think about using extra space to trade off time complexity\n2. For each number, calculate what number you need to find\n3. Hash maps provide O(1) lookup time",
            "estimated_time": 600,  # 10 minutes
            "input_examples": [
                "[2,7,11,15], 9",
                "[3,2,4], 6",
                "[3,3], 6"
            ],
            "output_examples": [
                "[0,1]",
                "[1,2]",
                "[0,1]"
            ],
            "constraints": "2 <= nums.length <= 10^4\n-10^9 <= nums[i] <= 10^9\n-10^9 <= target <= 10^9\nOnly one valid answer exists"
        },
        {
            "title": "Reverse a String",
            "description": "Write a function that reverses a string. The input string is given as an array of characters s. You must do this by modifying the input array in-place with O(1) extra memory.",
            "difficulty": DifficultyLevel.BEGINNER,
            "category": "algorithms",
            "solution": "Use two pointers approach. One pointer starts from the beginning and another from the end. Swap elements and move pointers toward each other.",
            "hints": "1. Consider two pointers technique\n2. Start one pointer at index 0 and another at last index\n3. Swap elements and move pointers inward",
            "estimated_time": 300,  # 5 minutes
            "input_examples": [
                '["h","e","l","l","o"]',
                '["H","a","n","n","a","h"]'
            ],
            "output_examples": [
                '["o","l","l","e","h"]',
                '["h","a","n","n","a","H"]'
            ],
            "constraints": "1 <= s.length <= 10^5\ns[i] is a printable ascii character"
        },
        {
            "title": "Valid Parentheses",
            "description": "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid. An input string is valid if: Open brackets must be closed by the same type of brackets. Open brackets must be closed in the correct order.",
            "difficulty": DifficultyLevel.BEGINNER,
            "category": "data_structures",
            "solution": "Use a stack to keep track of opening brackets. When encountering closing brackets, check if they match the most recent opening bracket.",
            "hints": "1. Stack is perfect for matching pairs\n2. Push opening brackets onto stack\n3. Pop when encountering closing brackets",
            "estimated_time": 420  # 7 minutes
        },
        
        # Intermediate Questions
        {
            "title": "Binary Tree Inorder Traversal",
            "description": "Given the root of a binary tree, return the inorder traversal of its nodes' values. Try to implement both recursive and iterative solutions.",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "category": "data_structures",
            "solution": "Inorder traversal visits nodes in the order: left subtree, root, right subtree. Can be implemented recursively or iteratively using a stack.",
            "hints": "1. Recursive approach is simpler\n2. For iterative, use explicit stack to simulate recursion\n3. Inorder: Left -> Root -> Right",
            "estimated_time": 600  # 10 minutes
        },
        {
            "title": "Container With Most Water",
            "description": "You are given an integer array height of length n. There are n vertical lines drawn such that the two endpoints of the ith line are (i, 0) and (i, height[i]). Find two lines that together with the x-axis form a container, such that the container contains the most water. Return the maximum amount of water a container can store.",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "category": "algorithms",
            "solution": "Use two pointers approach. Start with pointers at both ends. Move the pointer with smaller height inward to potentially find a larger area.",
            "hints": "1. Two pointers technique\n2. Start with maximum width\n3. Move the shorter line inward to possibly increase area",
            "estimated_time": 900  # 15 minutes
        },
        {
            "title": "Letter Combinations of a Phone Number",
            "description": "Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent. Return the answer in any order. A mapping of digits to letters (just like on the telephone buttons) is given below.",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "category": "algorithms",
            "solution": "Use backtracking to generate all possible combinations. For each digit, try all possible letters it maps to.",
            "hints": "1. Backtracking approach works well here\n2. Map digits to letters first\n3. At each step, try all possible letters for current digit",
            "estimated_time": 720  # 12 minutes
        },
        
        # Advanced Questions
        {
            "title": "Median of Two Sorted Arrays",
            "description": "Given two sorted arrays nums1 and nums2 of size m and n respectively, return the median of the two sorted arrays. The overall run time complexity should be O(log (m+n)).",
            "difficulty": DifficultyLevel.ADVANCED,
            "category": "algorithms",
            "solution": "Use binary search to partition both arrays such that elements on the left are smaller than elements on the right. Achieve O(log(min(m,n))) time complexity.",
            "hints": "1. Binary search on the smaller array\n2. Partition both arrays so left elements <= right elements\n3. Handle edge cases where partition is at start/end",
            "estimated_time": 1200  # 20 minutes
        },
        {
            "title": "LRU Cache Design",
            "description": "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache. Implement the LRUCache class with methods: LRUCache(int capacity), int get(int key), void put(int key, int value).",
            "difficulty": DifficultyLevel.ADVANCED,
            "category": "data_structures",
            "solution": "Use a combination of HashMap and Doubly Linked List. HashMap provides O(1) access, DLL maintains order of usage.",
            "hints": "1. Need O(1) for both get and put operations\n2. Combine HashMap with Doubly Linked List\n3. Head for most recently used, Tail for least recently used",
            "estimated_time": 1500  # 25 minutes
        },
        {
            "title": "Word Ladder",
            "description": "A transformation sequence from word beginWord to word endWord using a dictionary wordList is a sequence of words beginWord -> s1 -> s2 -> ... -> sk such that: Every adjacent pair of words differs by a single letter. Every si for 1 <= i <= k is in wordList. Given beginWord, endWord, and wordList, return the number of words in the shortest transformation sequence from beginWord to endWord, or 0 if no such sequence exists.",
            "difficulty": DifficultyLevel.ADVANCED,
            "category": "algorithms",
            "solution": "Model as a graph problem and use BFS to find shortest path. Each word is a node, and edges connect words differing by one letter.",
            "hints": "1. Graph problem - each word is a node\n2. BFS for shortest path\n3. Efficient neighbor generation with wildcards",
            "estimated_time": 1200  # 20 minutes
        }
    ]
    
    # Check if questions already exist
    beginner_count = len(get_dsa_questions_by_difficulty(db, "beginner"))
    if beginner_count == 0:
        for q_data in sample_questions:
            # Check if question already exists
            existing = db.query(DSAQuestion).filter(DSAQuestion.title == q_data['title']).first()
            if not existing:
                question = DSAQuestion(**q_data)
                db.add(question)
        
        db.commit()
        print(f"Loaded {len(sample_questions)} sample DSA questions into the database")
    else:
        print("Sample questions already exist in the database")