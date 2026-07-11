"""
text_variation_bank.py
Campus Innovation & Engagement Intelligence Hub — Phase 1, Day 13

Reusable variation banks for hybrid text generation.
No external dependencies.
"""

# ── Sectors ───────────────────────────────────────────────────────────────────

SECTORS = ["healthtech", "fintech", "edtech", "agritech", "climate", "mobility"]

# ── Problem areas: {sector: [problem phrase, ...]} ────────────────────────────

PROBLEM_AREAS: dict[str, list[str]] = {
    "healthtech": [
        "high patient no-show rates at urban clinics",
        "delayed diagnosis due to fragmented medical records",
        "poor medication adherence among chronic-disease patients",
        "lack of affordable specialist access in Tier-2 cities",
        "manual follow-up workflows overloading nursing staff",
        "diagnostic bottlenecks in radiology departments",
    ],
    "fintech": [
        "thin-file borrowers excluded from formal credit channels",
        "MSME cash-flow disruption from invoice payment delays",
        "gig workers without access to micro-insurance products",
        "high remittance fees for rural migrant workers",
        "manual reconciliation slowing B2B payment cycles",
        "credit invisibility among self-help group members",
    ],
    "edtech": [
        "first-generation learners unable to afford quality coaching",
        "high dropout rates in online upskilling programmes",
        "limited placement outcomes for non-metro engineering graduates",
        "low learning retention in traditional LMS platforms",
        "inadequate vernacular content for rural students",
        "employer-readiness gaps among fresh graduates",
    ],
    "agritech": [
        "smallholder farmers receiving a fraction of consumer prices",
        "post-harvest losses exceeding 25% in perishable supply chains",
        "late pest detection causing significant crop damage",
        "lack of collateral-free credit for agricultural inputs",
        "weather-driven yield uncertainty with no risk cover",
        "market information asymmetry between farmers and traders",
    ],
    "climate": [
        "untapped commercial rooftop solar potential in Indian cities",
        "municipal solid waste processed at a loss with no recovery value",
        "industrial energy wastage invisible to operations managers",
        "EV charging deserts on National Highway corridors",
        "carbon accounting done manually on disconnected spreadsheets",
        "water leakage in urban distribution networks going undetected",
    ],
    "mobility": [
        "first-mile and last-mile gaps in public transit networks",
        "fleet utilisation below 60% due to poor route optimisation",
        "freight matching inefficiency between transporters and shippers",
        "long vehicle idle times at logistics hubs causing emissions",
        "driver fatigue monitoring absent from commercial fleets",
        "cold-chain integrity failures in pharmaceutical distribution",
    ],
}

# ── Target users: {sector: [user phrase, ...]} ────────────────────────────────

TARGET_USERS: dict[str, list[str]] = {
    "healthtech": [
        "primary healthcare centres in semi-urban districts",
        "district hospitals seeking digital patient management",
        "corporate HR teams managing employee wellness",
        "independent pharmacists in Tier-2 cities",
        "public radiology departments with large backlogs",
    ],
    "fintech": [
        "MSMEs with annual turnover under ₹5 crore",
        "food-delivery and ride-share gig workers",
        "self-help groups in rural Maharashtra and Tamil Nadu",
        "small manufacturers needing working-capital liquidity",
        "salaried employees with no formal credit history",
    ],
    "edtech": [
        "Class 11 and 12 students in Tier-3 cities",
        "engineering graduates seeking IT placements",
        "working professionals upskilling for data roles",
        "rural school teachers with limited digital training",
        "corporates running internal capability programmes",
    ],
    "agritech": [
        "smallholder farmers with 1 to 5 acres in southern India",
        "farmer producer organisations managing 500-plus members",
        "food processors needing traceable raw-material supply",
        "state agriculture departments running subsidy schemes",
        "agri-input retailers supplying last-mile districts",
    ],
    "climate": [
        "SMEs with rooftop area over 2,000 sq ft",
        "municipal corporations processing 50 to 200 tonnes per day",
        "manufacturing units with monthly electricity bills above ₹5 lakh",
        "highway dhaba chains seeking EV charging partnerships",
        "real-estate developers targeting green building certification",
    ],
    "mobility": [
        "regional transport corporations managing mixed fleets",
        "e-commerce companies with dense last-mile delivery requirements",
        "pharmaceutical distributors needing cold-chain compliance",
        "logistics aggregators matching spot freight capacity",
        "urban commuters underserved by existing transit options",
    ],
}

# ── Value propositions: {sector: [value phrase, ...]} ────────────────────────

VALUE_PROPOSITIONS: dict[str, list[str]] = {
    "healthtech": [
        "reduces patient no-show rates by 40% through automated reminders",
        "cuts diagnostic turnaround time with AI-prioritised worklists",
        "improves medication adherence through personalised nudge workflows",
        "extends specialist reach via asynchronous teleconsultation",
        "unifies patient records across multiple care providers",
    ],
    "fintech": [
        "underwrites credit using GST and UPI transaction history",
        "accelerates invoice settlement by embedding discounting at checkout",
        "delivers pay-per-use micro-insurance at point of gig assignment",
        "reduces remittance cost by 60% through NBFC-backed corridors",
        "automates reconciliation via direct Tally and Zoho integration",
    ],
    "edtech": [
        "increases placement rates by matching learners to live job briefs",
        "improves retention through gamified cohort accountability pods",
        "delivers vernacular content in six Indian languages with adaptive pacing",
        "bridges employer-readiness gaps with outcome-linked assessments",
        "reduces coaching costs by 70% through live online cohort batches",
    ],
    "agritech": [
        "connects farmer producer organisations directly to institutional buyers",
        "detects pest infestation 10 days early using satellite imagery",
        "enables warehouse-receipt financing without land-title collateral",
        "reduces post-harvest loss through IoT-enabled cold-chain alerts",
        "provides real-time mandi price intelligence to reduce intermediary capture",
    ],
    "climate": [
        "deploys rooftop solar for SMEs with zero upfront capital",
        "converts municipal waste to compost and RDF at zero net cost",
        "monitors industrial energy consumption with ML anomaly detection",
        "rolls out modular fast-charging hubs via highway franchise partners",
        "automates carbon accounting from IoT sensor data",
    ],
    "mobility": [
        "improves fleet utilisation by 25% using real-time route intelligence",
        "matches freight capacity to shippers in under three minutes",
        "reduces cold-chain failures through predictive temperature alerts",
        "cuts idle-time emissions by optimising hub dispatch sequencing",
        "bridges first-mile gaps through hyperlocal electric vehicle pods",
    ],
}

# ── Technology tags: {sector: [tag, ...]} ────────────────────────────────────

TECHNOLOGY_TAGS: dict[str, list[str]] = {
    "healthtech": ["ABDM-compliant FHIR APIs", "NLP symptom extraction", "CNN diagnostic model",
                   "WhatsApp-native UX", "federated learning", "wearable sensor integration"],
    "fintech":    ["account aggregator framework", "GST analytics pipeline", "ML fraud detection",
                   "UPI payment rails", "RBI-compliant data localisation", "NBFC co-lending API"],
    "edtech":     ["adaptive learning engine", "NLP doubt resolution", "proctored assessment",
                   "video compression for low-bandwidth", "skills-graph mapping", "LMS integration"],
    "agritech":   ["multispectral satellite imagery", "IoT soil sensors", "blockchain traceability",
                   "USSD feature-phone interface", "warehouse receipt system", "weather API integration"],
    "climate":    ["IoT power monitoring", "SCADA integration", "digital twin simulation",
                   "satellite rooftop detection", "carbon credit registry API", "DISCOM net-metering"],
    "mobility":   ["real-time GPS telemetry", "route optimisation engine", "IoT temperature sensors",
                   "freight matching algorithm", "driver behaviour analytics", "EV fleet management"],
}

# ── Pitch sentence frame families ─────────────────────────────────────────────

PITCH_FRAMES: list[str] = [
    # Frame A: problem → solution → who benefits
    "{problem_area} is a critical gap for {target_user}. "
    "We {value_proposition} using {tech1} and {tech2}. "
    "Our platform creates measurable outcomes for {target_user} from day one.",

    # Frame B: user-first → pain → remedy
    "{target_user} face a persistent challenge: {problem_area}. "
    "{entity_name} addresses this directly by delivering a solution that {value_proposition}. "
    "Built on {tech1}, the system integrates seamlessly into existing workflows.",

    # Frame C: outcome-first → mechanism → user
    "By building a system that {value_proposition}, {entity_name} tackles "
    "{problem_area} at scale. "
    "Powered by {tech1} and {tech2}, the platform is purpose-built for {target_user}.",

    # Frame D: context → gap → approach
    "{problem_area} remains unresolved for most {target_user}. "
    "Existing tools fail to address this because they lack the intelligence layer "
    "our approach provides. "
    "{entity_name} uses {tech1} to {value_proposition} while reducing operational burden.",

    # Frame E: thesis statement → evidence → tech
    "The market opportunity in {sector} is driven by {problem_area}. "
    "{entity_name} has validated that {target_user} urgently need a solution that "
    "{value_proposition}. "
    "Our core technology stack includes {tech1} and {tech2}.",

    # Frame F: comparative — indirect
    "Unlike generic platforms, {entity_name} is designed specifically for {target_user} "
    "struggling with {problem_area}. "
    "We {value_proposition}, leveraging {tech1} for precision and scale.",
]

# ── Investor mandate frame families ──────────────────────────────────────────

INVESTOR_MANDATE_FRAMES: list[str] = [
    # Thesis-driven
    "We invest in {stage}-stage {sector_focus} companies where the founding team has "
    "deep domain expertise and a clear path to {outcome_phrase}. "
    "Our thesis centres on {interest_theme1} and {interest_theme2}.",

    # Operator-value-add
    "Having built and scaled {sector_focus} businesses ourselves, we bring operational "
    "value beyond capital to {stage}-stage founders. "
    "We are particularly excited about {interest_theme1} in the {sector_focus} space.",

    # Market-outcome-driven
    "We back {stage}-stage startups solving large, underserved problems in {sector_focus}. "
    "Our decision framework weights {interest_theme1} and {interest_theme2} most heavily. "
    "Portfolio companies typically achieve {outcome_phrase} within 18 months.",

    # Portfolio-fit
    "Our {sector_focus} portfolio focuses on {stage} companies with strong unit economics "
    "from early on. "
    "We look for founders who complement our existing investments in {interest_theme1}.",
]

# ── Mentor mandate frame families ─────────────────────────────────────────────

MENTOR_MANDATE_FRAMES: list[str] = [
    # Hands-on builder
    "I work best with early-stage founders who need a hands-on thinking partner. "
    "My background in {domain} lets me help with {support1} and {support2} in a practical way. "
    "I prefer weekly working sessions over one-off advice.",

    # Strategic advisor
    "With experience across {domain}, I advise founders on {support1} at the strategic level. "
    "I engage best when a founder has a clear question rather than an open-ended challenge. "
    "I can also open doors in {domain} through my network.",

    # Domain specialist
    "I specialise in {domain} and offer deep guidance on {support1}. "
    "Founders I mentor typically need help navigating {support2} for the first time. "
    "I am available for structured monthly reviews and async document feedback.",

    # Network connector
    "My primary value to founders is network access in {domain}. "
    "I help with {support1} by connecting the right people at the right time. "
    "I also support {support2} through introductions to investors and enterprise buyers.",
]

# ── Investor interest themes ───────────────────────────────────────────────────

INVESTOR_INTEREST_THEMES: dict[str, list[str]] = {
    "healthtech": ["preventive health infrastructure", "rural diagnostic access",
                   "AI-assisted clinical workflows", "pharma supply-chain digitisation"],
    "fintech":    ["alternative credit underwriting", "embedded insurance",
                   "MSME working-capital solutions", "cross-border payment corridors"],
    "edtech":     ["outcome-linked skilling", "vernacular content delivery",
                   "B2B corporate learning", "assessment and credentialing"],
    "agritech":   ["FPO-linked market linkage", "precision-input advisory",
                   "agricultural risk products", "post-harvest supply chains"],
    "climate":    ["distributed renewable energy", "waste valorisation",
                   "industrial decarbonisation", "carbon markets infrastructure"],
    "mobility":   ["urban mobility as a service", "EV fleet transition",
                   "logistics tech for SMEs", "cold-chain compliance"],
}

# ── Mentor support styles ──────────────────────────────────────────────────────

MENTOR_SUPPORT_STYLES: dict[str, list[str]] = {
    "healthtech": ["regulatory pathway navigation", "hospital partnership development",
                   "clinical validation study design", "B2B sales to institutional buyers"],
    "fintech":    ["RBI and SEBI compliance strategy", "co-lending partnership structuring",
                   "underwriting model review", "investor pitch preparation"],
    "edtech":     ["content-to-placement curriculum design", "B2B school and college sales",
                   "learning-outcome measurement", "regional market expansion"],
    "agritech":   ["FPO and cooperative engagement", "state government pilots",
                   "agri-commodity market dynamics", "last-mile distribution strategy"],
    "climate":    ["DISCOM and regulatory engagement", "MNRE scheme application",
                   "carbon credit project design", "impact measurement frameworks"],
    "mobility":   ["fleet operator partnerships", "transport regulator engagement",
                   "telematics and IoT integration", "multimodal product design"],
}

# ── Investor outcome phrases ──────────────────────────────────────────────────

INVESTOR_OUTCOME_PHRASES: list[str] = [
    "₹1 crore ARR",
    "a fundable Series A",
    "10,000 paying users",
    "a signed enterprise contract",
    "profitability on unit economics",
    "a government pilot at scale",
]

# ── Stage bands ───────────────────────────────────────────────────────────────

STAGES = ["pre-seed", "seed", "Series A", "grant-stage"]

# ── Check size bands ──────────────────────────────────────────────────────────

CHECK_SIZES = ["₹25L–₹1Cr", "₹1Cr–₹3Cr", "₹3Cr–₹10Cr", "₹10Cr+", "advisory only"]