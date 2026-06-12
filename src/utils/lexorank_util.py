
class LexorankUtil:
    prev_rank_default: str = 'a'
    next_rank_default: str = 'z'

    @staticmethod
    def get_lexorank_between(prev_rank:str|None, next_rank:str|None) -> str:
        """Calculates a string lexically positioned between prev_rank and nex_rank."""
        if not prev_rank:
            prev_rank = LexorankUtil.prev_rank_default
        if not next_rank:
            next_rank = LexorankUtil.next_rank_default

        result = []
        i = 0

        #Loop through the strings until a midpoint character can be inserted
        while True:
            p_char = prev_rank[i] if i < len(prev_rank) else LexorankUtil.prev_rank_default
            n_char = next_rank[i] if i < len(next_rank) else LexorankUtil.next_rank_default

            p_val = ord(p_char)
            n_val = ord(n_char)

            # If there is space between characters, pick the middle one
            if n_val - p_val > 1:
                mid_val = p_val + (n_val - p_val) // 2
                result.append(chr(mid_val))
                break
            else:
                # If characters are adjacent or identical, append the current character
                # and move to the next position to find space
                result.append(p_val)
                if p_char != n_char and i >= len(prev_rank) - 1:
                    result.append(chr((ord('a') + ord('z')) // 2))
                    break

            i += 1

        return ''.join(result)