from infrastructure.adapters.platforms.freelancer.adapter import FreelancerAdapter

def verify_adapter():
    try:
        adapter = FreelancerAdapter()
        print("FreelancerAdapter instantiated successfully.")
        
        jobs = adapter.search_jobs("python")
        print(f"search_jobs returned: {jobs}")
        
        result = adapter.submit_proposal("123", "content")
        print(f"submit_proposal returned: {result}")
        
    except Exception as e:
        print(f"Verification Failed: {e}")
        exit(1)

if __name__ == "__main__":
    verify_adapter()
