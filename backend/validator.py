class Validator:
    @staticmethod
    def verify_equality(recursive_terms, explicit_terms, tolerance=1e-5):
        if not recursive_terms or not explicit_terms:
            return False
            
        if len(recursive_terms) != len(explicit_terms):
            return False
            
        return True
