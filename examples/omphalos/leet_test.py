class Solution:
    def maxVowels(self, s: str, k: int) -> int:
        word = list(s)
        count = 0
        v_count = 0
        while len(word) >= k:
            sub = word[:k]
            print("Sub:", sub)
            
            for elem in sub:
                if elem in "aeiou":
                    v_count += 1
                    print(f"Found vowel: {elem}, current vowel count: {v_count}")
        
            if v_count >= (k-1):
                count += 1
                print(f"Vowel count {v_count} equals k-1 ({k-1}), incrementing count to {count}")
            v_count = 0
        
            word.pop(0)
        return count

if __name__ == "__main__":
    solution = Solution()
    
    test_cases = [
        #("abciiidef", 3),
        ("aeiou", 2),
        ("leetcode", 3)
    ]
    
    for i, (s, k) in enumerate(test_cases, 1):
        print(f"--- Test Case {i} ---")
        print(f"s = \"{s}\", k = {k}")
        try:
            result = solution.maxVowels(s, k)
            print(f"Result: {result}\n")
        except Exception as e:
            print(f"Error during execution: {type(e).__name__}: {e}\n")