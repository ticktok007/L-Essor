# matching/test_pairs.py

GOOD_PAIRS = [
    {
        "sector": "HealthTech",
        "startup_pitch": "AI-powered diagnostics for early detection of diabetic retinopathy.",
        "investor_mandate": "We focus on digital health, medical imaging, and chronic disease management."
    },
    {
        "sector": "FinTech",
        "startup_pitch": "Decentralized credit scoring for MSMEs using alternative transaction data.",
        "investor_mandate": "Backing next-gen financial infrastructure, neo-banking, and DeFi platforms."
    },
    {
        "sector": "SaaS",
        "startup_pitch": "Collaborative enterprise platform for automated procurement workflows.",
        "investor_mandate": "Our thesis targets B2B software, productivity tools, and cloud infrastructure."
    },
    {
        "sector": "Climate",
        "startup_pitch": "Optimizing energy distribution for residential solar microgrids using IoT.",
        "investor_mandate": "Investing in renewable energy, carbon capture, and grid efficiency technologies."
    }
]

BAD_PAIRS = [
    {
        "startup_pitch": "AI diagnostics for medical imaging.",
        "investor_mandate": "Purely focused on late-stage retail and e-commerce expansion."
    },
    {
        "startup_pitch": "Blockchain payments.",
        "investor_mandate": "Early-stage agricultural biotechnology and soil health sensors."
    }
]