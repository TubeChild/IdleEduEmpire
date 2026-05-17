from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BuildingDef:
    name: str
    desc: str
    base_cost: float
    base_kps: float
    unlock_at: float


@dataclass
class UpgradeDef:
    name: str
    desc: str
    cost: float
    target: str
    mult: float


@dataclass
class SkillDef:
    id: str
    name: str
    desc: str
    cost: int
    requires: Optional[str]
    effect_type: str
    effect_target: str
    effect_value: float
    path: str = "Foundation"


@dataclass
class AchievementDef:
    id: str
    name: str
    desc: str
    grade: str
    check: str
    check_target: str
    check_value: float
    merit_reward: int = 1


# ── Buildings (13 total) ──────────────────────────────────────────────────────

BUILDINGS: list[BuildingDef] = [
    BuildingDef("Classroom",           "Students learn the basics",                   10,                    0.1,          0),
    BuildingDef("Library",             "Books that expand the mind",                  120,                   0.5,          5),
    BuildingDef("Science Lab",         "Experiments accelerate discovery",            1_300,                 4.0,          60),
    BuildingDef("Computer Lab",        "Technology multiplies output",                14_000,                20.0,         600),
    BuildingDef("Sports Hall",         "Healthy body, healthy mind",                  150_000,               100.0,        6_000),
    BuildingDef("Art Studio",          "Creativity unlocks new thinking",             1_600_000,             500.0,        60_000),
    BuildingDef("University Wing",     "Higher education at scale",                   22_000_000,            3_000.0,      600_000),
    BuildingDef("Research Centre",     "Frontier of human knowledge",                 350_000_000,           20_000.0,     6_000_000),
    # Late-game buildings
    BuildingDef("Innovation Hub",      "Where disciplines collide and spark",         5_250_000_000,         300_000.0,    70_000_000),
    BuildingDef("Space Academy",       "Reaching beyond the atmosphere",              78_750_000_000,        4_500_000.0,  700_000_000),
    BuildingDef("World Campus",        "Knowledge without borders",                   1_181_250_000_000,     67_500_000.0, 7_000_000_000),
    BuildingDef("Quantum Institute",   "Harnessing the fabric of reality",            17_718_750_000_000,    1_012_500_000.0, 70_000_000_000),
    BuildingDef("Nexus of Knowledge",  "The sum of all human understanding",          265_781_250_000_000,   15_187_500_000.0, 700_000_000_000),
]

# ── Upgrades (24 total) ───────────────────────────────────────────────────────

UPGRADES: list[UpgradeDef] = [
    # Classroom (3)
    UpgradeDef("Better Textbooks",      "Classrooms × 2 KP/s",        100,                  "Classroom",       2.0),
    UpgradeDef("Interactive Boards",    "Classrooms × 2 KP/s",        600,                  "Classroom",       2.0),
    UpgradeDef("Dedicated Teachers",    "Classrooms × 2 KP/s",        12_000,               "Classroom",       2.0),
    # Library (3)
    UpgradeDef("Rare Book Collection",  "Libraries × 2 KP/s",         1_200,                "Library",         2.0),
    UpgradeDef("E-Library Access",      "Libraries × 2 KP/s",         6_000,                "Library",         2.0),
    UpgradeDef("24hr Study Zone",       "Libraries × 2 KP/s",         60_000,               "Library",         2.0),
    # Science Lab (2)
    UpgradeDef("New Equipment",         "Science Labs × 2 KP/s",      14_000,               "Science Lab",     2.0),
    UpgradeDef("PhD Researchers",       "Science Labs × 2 KP/s",      130_000,              "Science Lab",     2.0),
    # Computer Lab (2)
    UpgradeDef("Faster Internet",       "Computer Labs × 2 KP/s",     140_000,              "Computer Lab",    2.0),
    UpgradeDef("AI Tutoring Suite",     "Computer Labs × 2 KP/s",     1_400_000,            "Computer Lab",    2.0),
    # Sports Hall (2) — new
    UpgradeDef("Fitness Curriculum",    "Sports Halls × 2 KP/s",      15_000_000,           "Sports Hall",     2.0),
    UpgradeDef("Championship Teams",    "Sports Halls × 2 KP/s",      150_000_000,          "Sports Hall",     2.0),
    # Art Studio (2) — new
    UpgradeDef("Digital Art Tools",     "Art Studios × 2 KP/s",       160_000_000,          "Art Studio",      2.0),
    UpgradeDef("Artist Residency",      "Art Studios × 2 KP/s",       1_600_000_000,        "Art Studio",      2.0),
    # University Wing (2) — new
    UpgradeDef("Lecture Series",        "University Wings × 2 KP/s",  2_200_000_000,        "University Wing", 2.0),
    UpgradeDef("Global Partnerships",   "University Wings × 2 KP/s",  22_000_000_000,       "University Wing", 2.0),
    # Research Centre (2) — new
    UpgradeDef("Supercomputer",         "Research Centres × 2 KP/s",  35_000_000_000,       "Research Centre", 2.0),
    UpgradeDef("Breakthrough Labs",     "Research Centres × 2 KP/s",  350_000_000_000,      "Research Centre", 2.0),
    # Innovation Hub (1) — new
    UpgradeDef("Startup Incubator",     "Innovation Hubs × 2 KP/s",   525_000_000_000,      "Innovation Hub",  2.0),
    # Space Academy (1) — new
    UpgradeDef("Orbital Curriculum",    "Space Academies × 2 KP/s",   7_875_000_000_000,    "Space Academy",   2.0),
    # Innovation Hub (2 more) — parity
    UpgradeDef("Cross-Disciplinary Labs",  "Innovation Hubs × 2 KP/s",   5_250_000_000_000,    "Innovation Hub",    2.0),
    UpgradeDef("Breakthrough Accelerator", "Innovation Hubs × 2 KP/s",   52_500_000_000_000,   "Innovation Hub",    2.0),
    # Space Academy (2 more) — parity
    UpgradeDef("Zero-G Laboratory",        "Space Academies × 2 KP/s",   78_750_000_000_000,   "Space Academy",     2.0),
    UpgradeDef("Deep Space Program",       "Space Academies × 2 KP/s",   787_500_000_000_000,  "Space Academy",     2.0),
    # World Campus (2) — new
    UpgradeDef("Global Exchange",          "World Campuses × 2 KP/s",    118_125_000_000_000,  "World Campus",      2.0),
    UpgradeDef("Universal Curriculum",     "World Campuses × 2 KP/s",    1_181_250_000_000_000,"World Campus",      2.0),
    # Quantum Institute (2) — new
    UpgradeDef("Entanglement Lab",         "Quantum Institutes × 2 KP/s",1_771_875_000_000_000,"Quantum Institute", 2.0),
    UpgradeDef("Reality Engine",           "Quantum Institutes × 2 KP/s",17_718_750_000_000_000,"Quantum Institute",2.0),
    # Nexus of Knowledge (2) — new
    UpgradeDef("Omniscience Protocol",     "Nexuses of Knowledge × 2 KP/s",26_578_125_000_000_000,"Nexus of Knowledge",2.0),
    UpgradeDef("The Final Theorem",        "Nexuses of Knowledge × 2 KP/s",265_781_250_000_000_000,"Nexus of Knowledge",2.0),
    # Click upgrades (4)
    UpgradeDef("Sharp Pencil",          "Click power × 2",             50,                  "click",           2.0),
    UpgradeDef("Fountain Pen",          "Click power × 2",             600,                 "click",           2.0),
    UpgradeDef("Laptop",                "Click power × 2",             6_000,               "click",           2.0),
    UpgradeDef("Gaming Tablet",         "Click power × 2",             60_000,              "click",           2.0),
]

# ── Skills (30 total — 13 Foundation + 17 new path skills) ───────────────────

SKILLS: list[SkillDef] = [
    # ── Foundation (original 13) ──────────────────────────────────────────────
    SkillDef("eager_student",  "Eager Student",    "+2 base click power",               1,  None,            "click_base",       "",                2.0),
    SkillDef("speed_reader",   "Speed Reader",     "All buildings +10% KP/s",           2,  None,            "global_kps",       "",                0.10),
    SkillDef("class_rep",      "Class Rep",        "Classrooms +25% KP/s",              2,  None,            "building_bonus",   "Classroom",       0.25),
    SkillDef("library_card",   "Library Card",     "Libraries +25% KP/s",               2,  None,            "building_bonus",   "Library",         0.25),
    SkillDef("lab_safety",     "Lab Safety",       "Science Labs +25% KP/s",            3,  None,            "building_bonus",   "Science Lab",     0.25),
    SkillDef("tech_savvy",     "Tech Savvy",       "Computer Labs +25% KP/s",           3,  None,            "building_bonus",   "Computer Lab",    0.25),
    SkillDef("team_captain",   "Team Captain",     "Sports Hall +25% KP/s",             3,  None,            "building_bonus",   "Sports Hall",     0.25),
    SkillDef("study_group",    "Study Group",      "Offline earnings cap +2 hrs",       4,  None,            "offline_cap",      "",                2.0),
    SkillDef("deans_list",     "Dean's List",      "Click power × 3",                   5,  "eager_student", "click_mult",       "",                3.0),
    SkillDef("scholarship",    "Scholarship",      "Prestige diploma gain +50%",        6,  None,            "prestige_bonus",   "",                0.5),
    SkillDef("extra_credit",   "Extra Credit",     "+1 Merit per achievement",          5,  None,            "merit_bonus",      "",                1.0),
    SkillDef("valedictorian",  "Valedictorian",    "All KP/s × 1.5",                    8,  "speed_reader",  "global_kps_mult",  "",                1.5),
    SkillDef("perfect_score",  "Perfect Score",    "All KP/s × 2",                     12,  "valedictorian", "global_kps_mult",  "",                2.0),

    # ── Academic Excellence Path ──────────────────────────────────────────────
    SkillDef("academic_gw",   "Academic Excellence", "Unlock Academic path (+5% KPS)", 3,  "valedictorian", "global_kps",       "",                0.05, "Academic"),
    SkillDef("all_rounder",   "Well-Rounded",        "All buildings +20% KP/s",        5,  "academic_gw",   "global_kps",       "",                0.20, "Academic"),
    SkillDef("synergy_expert","Synergy Expert",       "All synergy bonuses ×2",         6,  "academic_gw",   "synergy_amp",      "",                1.0,  "Academic"),
    SkillDef("merit_master",  "Merit Master",         "+2 Merit per achievement",       6,  "academic_gw",   "merit_bonus",      "",                2.0,  "Academic"),
    SkillDef("dean_scholar",  "Dean's Scholar",       "Diploma gain +100% on prestige", 8,  "academic_gw",   "prestige_bonus",   "",                1.0,  "Academic"),

    # ── Innovation Path ───────────────────────────────────────────────────────
    SkillDef("innov_gw",       "Innovation Track",    "Unlock Innovation path (+5% KPS)", 3, "tech_savvy",  "global_kps",       "",                0.05, "Innovation"),
    SkillDef("research_synergy","Research Synergy",   "Research Centres +40% KP/s",     6,  "innov_gw",    "building_bonus",   "Research Centre", 0.40, "Innovation"),
    SkillDef("late_learner",   "Late Bloomer",        "Innovation Hubs +50% KP/s",      6,  "innov_gw",    "building_bonus",   "Innovation Hub",  0.50, "Innovation"),
    SkillDef("quantum_mind",   "Quantum Mindset",     "All KP/s × 1.25",                8,  "innov_gw",    "global_kps_mult",  "",                1.25, "Innovation"),

    # ── Prestige Mastery Path ─────────────────────────────────────────────────
    SkillDef("prestige_gw",   "Prestige Mastery",    "Unlock Prestige path (+5% KPS)",  5,  "scholarship",  "global_kps",       "",                0.05, "Prestige"),
    SkillDef("honor_scholar", "Honor Scholar",        "KPS += 25% × Honors held",       8,  "prestige_gw",  "honor_kps",        "",                0.25, "Prestige"),
    SkillDef("endow_speciali","Endow. Specialist",    "KPS += 50% × Endowments held",   10, "prestige_gw",  "endow_kps",        "",                0.50, "Prestige"),
    SkillDef("diploma_hoard", "Diploma Hoarder",      "Honors cost only 10 Diplomas",   8,  "prestige_gw",  "honor_rate",       "",                10.0, "Prestige"),

    # ── Active Learning Path ──────────────────────────────────────────────────
    SkillDef("active_gw",     "Active Learner",       "Unlock Active path (+3 click)",  2,  None,           "click_base",       "",                3.0,  "Active"),
    SkillDef("rapid_clicker", "Rapid Clicker",        "+5 base click power",            4,  "active_gw",    "click_base",       "",                5.0,  "Active"),
    SkillDef("focus_burst",   "Focus Burst",          "Offline cap +4 extra hours",     4,  "active_gw",    "offline_cap",      "",                4.0,  "Active"),
    SkillDef("combo_master",  "Combo Master",         "Max combo increased by 5",       5,  "active_gw",    "combo_cap_bonus",  "",                5.0,  "Active"),
    SkillDef("focus_pool",    "Focus Pool",           "+5 max Focus Points",            4,  "active_gw",    "focus_cap",        "",                5.0,  "Active"),
    SkillDef("focus_charge",  "Quick Charge",         "FP regens 50% faster",           5,  "focus_pool",   "focus_regen",      "",                0.5,  "Active"),

    # ── Mastery Path (very expensive, end-game) ───────────────────────────────
    SkillDef("mastery_gw",    "Grand Scholar",        "Unlock Mastery path — All KP/s +20%",  15, "perfect_score","global_kps",      "",                0.20, "Mastery"),
    SkillDef("deep_focus",    "Deep Focus",           "Offline earnings cap +24 hours",        15, "focus_burst",  "offline_cap",     "",                24.0, "Mastery"),
    SkillDef("cosmic_click",  "Cosmic Click",         "Click power ×20",                       35, "mastery_gw",   "click_mult",      "",                20.0, "Mastery"),
    SkillDef("zone_harmony",  "Zone Harmonics",       "All zones KP ×1.5",                     25, "all_rounder",  "global_kps_mult", "",                1.5,  "Mastery"),
    SkillDef("mult_stack",    "Multiplier Stack",     "All KP/s ×3",                           25, "mastery_gw",   "global_kps_mult", "",                3.0,  "Mastery"),
    SkillDef("prestige_vet",  "Prestige Veteran",     "Diploma gain +200% on prestige",        30, "dean_scholar", "prestige_bonus",  "",                2.0,  "Mastery"),
    SkillDef("time_warden",   "Time Warden",          "All KP/s ×5",                           40, "mult_stack",   "global_kps_mult", "",                5.0,  "Mastery"),
    SkillDef("omniscient",    "Omniscient",           "All KP/s ×10 — true mastery",           60, "time_warden",  "global_kps_mult", "",                10.0, "Mastery"),
]

# ── Achievements ─────────────────────────────────────────────────────────────

ACHIEVEMENTS: list[AchievementDef] = [
    # KP milestones
    AchievementDef("kp_1k",       "First Star",        "Earn 1,000 KP total",           "C",   "kp_total",       "",                  1_000,                  1),
    AchievementDef("kp_10k",      "Honour Roll",       "Earn 10,000 KP total",          "B",   "kp_total",       "",                  10_000,                 1),
    AchievementDef("kp_100k",     "Head of Class",     "Earn 100,000 KP total",         "B+",  "kp_total",       "",                  100_000,                2),
    AchievementDef("kp_1m",       "Summa Cum Laude",   "Earn 1 Million KP total",       "A",   "kp_total",       "",                  1_000_000,              2),
    AchievementDef("kp_5m",       "Five Million Strong","Earn 5 Million KP total",       "B+",  "kp_total",       "",                  5_000_000,              2),
    AchievementDef("kp_50m",      "Fifty Million Club","Earn 50 Million KP total",       "A",   "kp_total",       "",                  50_000_000,             2),
    AchievementDef("kp_1b",       "Nobel Prize",       "Earn 1 Billion KP total",       "A+",  "kp_total",       "",                  1_000_000_000,          3),
    AchievementDef("kp_100b",     "Trillion Scholar",  "Earn 100 Billion KP total",     "A+",  "kp_total",       "",                  100_000_000_000,        5),
    AchievementDef("kp_1t",       "Knowledge Titan",   "Earn 1 Trillion KP total",      "S",   "kp_total",       "",                  1_000_000_000_000,      8),
    AchievementDef("kp_1q",       "Infinite Mind",     "Earn 1 Quadrillion KP total",   "S+",  "kp_total",       "",                  1_000_000_000_000_000,  10),
    # Click milestones
    AchievementDef("click_10",    "Pencil Pusher",     "Click 10 times",                "C",   "clicks",         "",                  10,                     1),
    AchievementDef("click_100",   "Studious",          "Click 100 times",               "B",   "clicks",         "",                  100,                    1),
    AchievementDef("click_1k",    "Bookworm",          "Click 1,000 times",             "B+",  "clicks",         "",                  1_000,                  2),
    AchievementDef("click_10k",   "Study Machine",     "Click 10,000 times",            "A",   "clicks",         "",                  10_000,                 2),
    AchievementDef("click_100k",  "Speed Scholar",     "Click 100,000 times",           "A+",  "clicks",         "",                  100_000,                3),
    # Building counts — Classroom
    AchievementDef("own_class1",  "Open a Class",      "Buy 1 Classroom",               "C",   "building_count", "Classroom",         1,                      1),
    AchievementDef("own_class10", "School Day",        "Own 10 Classrooms",             "B",   "building_count", "Classroom",         10,                     1),
    AchievementDef("own_class50", "Mass Education",    "Own 50 Classrooms",             "A",   "building_count", "Classroom",         50,                     2),
    # Building counts — Library
    AchievementDef("own_lib1",    "Card Holder",       "Buy 1 Library",                 "C",   "building_count", "Library",           1,                      1),
    AchievementDef("own_lib10",   "Bibliophile",       "Own 10 Libraries",              "B",   "building_count", "Library",           10,                     1),
    # Building counts — other early buildings
    AchievementDef("own_sport1",  "Game Day",          "Buy 1 Sports Hall",             "C",   "building_count", "Sports Hall",       1,                      1),
    AchievementDef("own_sport10", "Team Spirit",       "Own 10 Sports Halls",           "B",   "building_count", "Sports Hall",       10,                     2),
    AchievementDef("own_art1",    "Creative Spark",    "Buy 1 Art Studio",              "C",   "building_count", "Art Studio",        1,                      1),
    AchievementDef("own_art10",   "Artistic Vision",   "Own 10 Art Studios",            "B",   "building_count", "Art Studio",        10,                     2),
    AchievementDef("own_uni1",    "Higher Learning",   "Buy 1 University Wing",         "B",   "building_count", "University Wing",   1,                      1),
    AchievementDef("own_uni10",   "Academic Empire",   "Own 10 University Wings",       "B+",  "building_count", "University Wing",   10,                     2),
    AchievementDef("own_res1",    "Frontier Seeker",   "Buy 1 Research Centre",         "B",   "building_count", "Research Centre",   1,                      2),
    AchievementDef("own_res10",   "Research Dynasty",  "Own 10 Research Centres",       "A",   "building_count", "Research Centre",   10,                     3),
    # Building counts — Science Lab
    AchievementDef("own_sci1",    "Lab Coat",          "Buy 1 Science Lab",             "C",   "building_count", "Science Lab",       1,                      0),
    AchievementDef("own_sci10",   "Scientific Method", "Own 10 Science Labs",           "B",   "building_count", "Science Lab",       10,                     1),
    # Extended Classroom & Library milestones
    AchievementDef("own_class100","Packed Halls",      "Own 100 Classrooms",            "A+",  "building_count", "Classroom",         100,                    3),
    AchievementDef("own_lib50",   "Endless Pages",     "Own 50 Libraries",              "A+",  "building_count", "Library",           50,                     2),
    # Late-game buildings
    AchievementDef("own_innov1",  "Innovator",         "Buy 1 Innovation Hub",          "A",   "building_count", "Innovation Hub",    1,                      3),
    AchievementDef("own_space1",  "Space Cadet",       "Buy 1 Space Academy",           "A+",  "building_count", "Space Academy",     1,                      4),
    AchievementDef("own_world1",  "Global Educator",   "Buy 1 World Campus",            "A+",  "building_count", "World Campus",      1,                      5),
    AchievementDef("own_quant1",  "Quantum Scholar",   "Buy 1 Quantum Institute",       "S",   "building_count", "Quantum Institute", 1,                      6),
    AchievementDef("own_nexus1",  "The Nexus",         "Buy 1 Nexus of Knowledge",      "S+",  "building_count", "Nexus of Knowledge",1,                      8),
    # Zone 10 — Hero World buildings
    AchievementDef("own_hero1",   "Hero Rising",       "Buy 1 Hero Academy",            "B",   "building_count", "Hero Academy",      1,                      1),
    AchievementDef("own_hero10",  "League of Scholars","Own 10 Hero Academies",         "A",   "building_count", "Hero Academy",      10,                     3),
    AchievementDef("own_dojo1",   "Enter the Dojo",    "Buy 1 Training Dojo",           "B",   "building_count", "Training Dojo",     1,                      1),
    AchievementDef("own_hq1",     "Heroes Need a Base","Buy 1 Hero HQ",                 "B+",  "building_count", "Hero HQ",           1,                      2),
    AchievementDef("own_arena1",  "The Crowd Goes Wild","Buy 1 Battle Arena",           "B",   "building_count", "Battle Arena",      1,                      1),
    AchievementDef("own_prison1", "Justice Served",    "Buy 1 Villain Prison",          "B+",  "building_count", "Villain Prison",    1,                      2),
    AchievementDef("own_citadel1","Champion Crowned",  "Buy 1 Champion's Citadel",      "S",   "building_count", "Champion's Citadel",1,                      6),
    # Campus milestones
    AchievementDef("all_bld",     "Full Campus",       "Own every building type once",  "A+",  "all_buildings",  "",                  1,                      3),
    AchievementDef("total_50",    "Campus Life",       "Own 50 buildings total",        "B+",  "total_buildings","",                  50,                     2),
    AchievementDef("total_100",   "Big Campus",        "Own 100 buildings total",       "A",   "total_buildings","",                  100,                    3),
    AchievementDef("total_200",   "Mega Campus",       "Own 200 buildings total",       "A+",  "total_buildings","",                  200,                    4),
    # Prestige milestones
    AchievementDef("prestige_1",  "Graduate!",         "Prestige once",                 "A",   "prestige",       "",                  1,                      3),
    AchievementDef("prestige_5",  "Alumni",            "Prestige 5 times",              "A+",  "prestige",       "",                  5,                      4),
    AchievementDef("prestige_10", "Veteran Scholar",   "Prestige 10 times",             "S",   "prestige",       "",                  10,                     5),
    # Combo
    AchievementDef("combo_max",   "Perfect Combo",     "Reach max combo (10+)",         "A",   "combo",          "",                  10,                     3),
    # Honors / Endowments
    AchievementDef("honor_1",     "Honors Graduate",   "Earn your first Honor",         "A+",  "honors",         "",                  1,                      4),
    AchievementDef("honor_5",     "Honor Society",     "Earn 5 Honors",                 "S",   "honors",         "",                  5,                      5),
    AchievementDef("endow_1",     "Endowed Chair",     "Earn your first Endowment",     "S",   "endowments",     "",                  1,                      7),
    AchievementDef("endow_3",     "Legacy Builder",    "Earn 3 Endowments",             "S+",  "endowments",     "",                  3,                      10),
    # Building star milestones
    AchievementDef("star_1",      "Rising Star",       "Reach 1-star on any building",  "A",   "star_level",     "",                  1,                      3),
    AchievementDef("star_2",      "Stargazer",         "Reach 2-star on any building",  "A+",  "star_level",     "",                  2,                      5),
    AchievementDef("star_3",      "Stellar Scholar",   "Reach 3-star on any building",  "S",   "star_level",     "",                  3,                      8),
    AchievementDef("star_4",      "Supernova",         "Reach 4-star on any building",  "S+",  "star_level",     "",                  4,                      12),
    # Scholars
    AchievementDef("scholars_1",  "Curious Minds",     "Hire your first Scholar",        "B+",  "scholars",       "",                  1,                      2),
    AchievementDef("scholars_5",  "The Faculty",       "Hire 5 Scholars",                "A",   "scholars",       "",                  5,                      4),
    AchievementDef("scholars_all","Timeless Wisdom",   "Hire all 12 Scholars",           "S",   "all_scholars",   "",                  1,                      10),
    # Faculty hire events
    AchievementDef("faculty_1",   "Staff Room",        "Collect a Faculty Hire event",   "A",   "faculty_count",  "",                  1,                      3),
    AchievementDef("faculty_5",   "Dream Team",        "Collect 5 Faculty Hire events",  "A+",  "faculty_count",  "",                  5,                      5),
    AchievementDef("faculty_10",  "World Class Staff", "Collect 10 Faculty Hire events", "S",   "faculty_count",  "",                  10,                     8),
    # Daily missions
    AchievementDef("daily_1",     "Daily Grind",       "Complete all 3 daily missions",  "B",   "daily_done",     "",                  1,                      2),
    AchievementDef("daily_7",     "Committed",         "Complete 7 full mission days",   "A",   "daily_done",     "",                  7,                      4),
    AchievementDef("daily_30",    "Perfect Attendance","Complete 30 full mission days",  "A+",  "daily_done",     "",                  30,                     6),
    # Seasons
    AchievementDef("seasons_all", "Four Seasons",      "Experience all four seasons",    "A",   "seasons_seen",   "",                  4,                      4),
    # Alumni Network
    AchievementDef("alumni_1",   "First Alumnus",     "Earn your first Alumni Point",   "A+",  "alumni_earned",  "",                  1,                      5),
    AchievementDef("alumni_3",   "Network Builder",   "Earn 3 Alumni Points",           "S",   "alumni_earned",  "",                  3,                      8),
    AchievementDef("alumni_5",   "Eternal Legacy",    "Earn 5 Alumni Points",           "S+",  "alumni_earned",  "",                  5,                      12),
    # Endgame prestige milestones
    AchievementDef("prestige_25","Century Scholar",   "Prestige 25 times",              "S",   "prestige",       "",                  25,                     10),
    AchievementDef("prestige_50","Eternal Student",   "Prestige 50 times",              "S+",  "prestige",       "",                  50,                     15),
    # Endgame building totals
    AchievementDef("total_1000", "Grand Campus",      "Own 1,000 buildings total",      "S",   "total_buildings","",                  1_000,                  8),
    # Research Legacy endgame loop
    AchievementDef("research_10","Researcher Emeritus","Buy 10 Research Legacy grants", "S+",  "research_legacy","",                  10,                     10),

    # ── Easy exploration (0 merit — just for the joy of discovery) ────────────
    AchievementDef("click_3",       "Here We Go",          "Click 3 times",                          "C",  "clicks",         "",               3,               0),
    AchievementDef("kp_50",         "Loose Change",        "Earn 50 KP",                             "C",  "kp_total",       "",               50,              0),
    AchievementDef("kp_500",        "Coffee Money",        "Earn 500 KP",                            "C",  "kp_total",       "",               500,             0),
    AchievementDef("total_3bld",    "A Humble Start",      "Own 3 buildings total",                  "C",  "total_buildings","",               3,               0),
    AchievementDef("total_5bld",    "Getting Somewhere",   "Own 5 buildings total",                  "C",  "total_buildings","",               5,               0),
    AchievementDef("upg_first",     "Textbook Purchase",   "Buy your first upgrade",                 "C",  "upgrades_count", "",               1,               0),
    AchievementDef("upg_5",         "Well Equipped",       "Buy 5 upgrades",                         "C",  "upgrades_count", "",               5,               0),
    AchievementDef("event_first",   "Breaking News",       "Collect your first event",               "C",  "events_collected","",              1,               0),
    AchievementDef("event_5",       "News Junkie",         "Collect 5 events",                       "C",  "events_collected","",              5,               0),
    AchievementDef("combo_3",       "On a Roll",           "Build a combo of 3",                     "C",  "combo",          "",               3,               0),
    AchievementDef("combo_5",       "Getting in the Groove","Reach a combo of 5",                   "C",  "combo",          "",               5,               0),
    AchievementDef("focus_first",   "In the Zone",         "Use a Focus ability",                    "C",  "focus_used",     "",               1,               0),
    AchievementDef("focus_5",       "Caffeinated",         "Use Focus abilities 5 times",            "C",  "focus_used",     "",               5,               0),
    AchievementDef("own_comp1",     "Connected",           "Buy 1 Computer Lab",                     "C",  "building_count", "Computer Lab",   1,               0),
    AchievementDef("upg_10",        "Well Stocked",        "Buy 10 upgrades",                        "B",  "upgrades_count", "",               10,              1),
    AchievementDef("click_50k",     "Relentless",          "Click 50,000 times",                     "A",  "clicks",         "",               50_000,          2),
    AchievementDef("own_innov10",   "Innovation Station",  "Own 10 Innovation Hubs",                 "A",  "building_count", "Innovation Hub", 10,              3),
    AchievementDef("own_space10",   "Fleet Commander",     "Own 10 Space Academies",                 "A+", "building_count", "Space Academy",  10,              4),
    AchievementDef("own_world10",   "Global Network",      "Own 10 World Campuses",                  "S",  "building_count", "World Campus",   10,              5),
    AchievementDef("own_quant10",   "Entanglement",        "Own 10 Quantum Institutes",              "S",  "building_count", "Quantum Institute",10,            6),
    AchievementDef("own_nexus10",   "Omniscient",          "Own 10 Nexuses of Knowledge",            "S+", "building_count", "Nexus of Knowledge",10,           8),
    AchievementDef("total_30",      "Mid-Sized Campus",    "Own 30 buildings total",                 "B",  "total_buildings","",               30,              1),
    AchievementDef("total_75",      "Sprawling Campus",    "Own 75 buildings total",                 "B+", "total_buildings","",               75,              2),
    AchievementDef("total_150",     "University Town",     "Own 150 buildings total",                "A",  "total_buildings","",               150,             3),
    AchievementDef("total_500",     "Metropolis",          "Own 500 buildings total",                "A+", "total_buildings","",               500,             5),

    # ── Funny / silly ─────────────────────────────────────────────────────────
    AchievementDef("click_42",      "The Answer",          "Click exactly 42 times",                 "C",  "clicks",         "",               42,              0),
    AchievementDef("click_360",     "Full Rotation",       "Click 360 times — knowledge goes in circles","C","clicks",      "",               360,             0),
    AchievementDef("click_999",     "Almost There",        "Click 999 times",                        "C",  "clicks",         "",               999,             0),
    AchievementDef("kp_2048",       "Power of Two",        "Earn 2,048 KP — may this game consume you","C","kp_total",       "",               2_048,           0),
    AchievementDef("dipl_69",       "Nice Diplomas",       "Accumulate exactly 69 Diplomas",         "B",  "diplomas",       "",               69,              0),
    AchievementDef("click_420",     "Study Break",         "Click 420 times — you earned a rest",    "C",  "clicks",         "",               420,             0),
    AchievementDef("click_9001",    "It's Over 9000",      "Click over 9,001 times",                 "B",  "clicks",         "",               9_001,           1),
    AchievementDef("click_69k",     "Nice.",               "Click 69,000 times",                     "A",  "clicks",         "",               69_000,          2),
    AchievementDef("kp_1337",       "Leet Scholar",        "Earn exactly 1,337 all-time KP",         "C",  "kp_total",       "",               1_337,           0),
    AchievementDef("focus_10",      "Overcaffeinated",     "Use Focus abilities 10 times",           "B",  "focus_used",     "",               10,              1),
    AchievementDef("focus_50",      "Living in Flow",      "Use Focus abilities 50 times",           "A",  "focus_used",     "",               50,              2),
    AchievementDef("event_20",      "Always Something",    "Collect 20 events",                      "B",  "events_collected","",              20,              1),
    AchievementDef("event_69",      "Nice Event",          "Collect 69 events",                      "A",  "events_collected","",              69,              2),
    AchievementDef("upg_all",       "Fully Loaded",        "Buy all standard upgrades",              "A",  "upgrades_count", "",               34,              3),
    AchievementDef("bld_x64",       "Uncle Works at Nintendo","Own 64 of any one building",          "A",  "max_single_bld", "",               64,              3),
    AchievementDef("bld_x100",      "Mass Production",     "Own 100 of any one building",            "A+", "max_single_bld", "",               100,             4),
    AchievementDef("daily_3",       "Routine",             "Complete 3 full mission days",           "B",  "daily_done",     "",               3,               2),
    AchievementDef("scholars_10",   "The Think Tank",      "Hire 10 Scholars",                       "A+", "scholars",       "",               10,              5),

    # ── Pop-culture / game references ─────────────────────────────────────────
    AchievementDef("ref_cookie",    "One More Cookie",     "Reach 1 Billion KP — the OG idle game would be proud",  "A",  "kp_total",  "",  1_000_000_000,    2),
    AchievementDef("ref_prestige_p","Butterfly Effect",    "Prestige for the first time — a whole new you",         "A",  "prestige",  "",  1,                0),
    AchievementDef("ref_minecraft", "Dirt Hut Scholar",    "Own 64 Classrooms — every journey starts small",        "A",  "building_count","Classroom", 64,   2),
    AchievementDef("ref_pokemon",   "Gotta Buy 'Em All",   "Own at least one of every building type",               "A+", "all_buildings","",   1,             3),
    AchievementDef("ref_darksouls", "You Died (and Reset)","Prestige 5 times — death and rebirth",                  "A+", "prestige",  "",  5,                0),
    AchievementDef("ref_montyhall", "Deal or No Deal",     "Own 3 Classrooms, 3 Libraries, and 3 Science Labs",     "B",  "total_buildings","",  9,            0),
    AchievementDef("ref_simcity",   "Mayor of Edu Town",   "Own 200 buildings total",                               "A",  "total_buildings","", 200,           2),
    AchievementDef("ref_idle_hero", "Idle Warrior",        "Earn KP while offline for the first time",              "B",  "prestige",  "",  1,                0),
    AchievementDef("ref_league",    "GG EZ",               "Prestige 10 times",                                     "S",  "prestige",  "",  10,               0),
    AchievementDef("ref_hl3",       "Half Knowledge 3",    "Earn exactly 3 Alumni Points — we waited so long",      "S",  "alumni_earned","", 3,              0),
    AchievementDef("ref_avengers",  "Assembled",           "Own 10 Hero Academies — heroes assemble!",               "S+", "building_count","Hero Academy", 10,  0),
    AchievementDef("ref_batman",    "I Am the Night School","Buy 1 Villain Prison — vengeance is academic",           "A",  "building_count","Villain Prison", 1,  0),
    AchievementDef("ref_xmen",      "Gifted Students",     "Own 1 Champion's Citadel — welcome, gifted one",  "S","building_count","Champion's Citadel",1,0),

    # ── Medium (2–4 merit) ────────────────────────────────────────────────────
    AchievementDef("upg_20",        "Knowledge Arsenal",   "Buy 20 upgrades",                        "B+", "upgrades_count", "",               20,              2),
    AchievementDef("event_10",      "Frequent Flyer",      "Collect 10 events",                      "B",  "events_collected","",              10,              2),
    AchievementDef("event_50",      "Event Horizon",       "Collect 50 events",                      "A",  "events_collected","",              50,              3),
    AchievementDef("focus_25",      "Sharp Mind",          "Use Focus abilities 25 times",           "B+", "focus_used",     "",               25,              2),
    AchievementDef("dipl_10",       "Diploma Collection",  "Accumulate 10 Diplomas",                 "B+", "diplomas",       "",               10,              2),
    AchievementDef("dipl_50",       "Diploma Hoarder",     "Accumulate 50 Diplomas",                 "A",  "diplomas",       "",               50,              3),
    AchievementDef("dipl_100",      "Diploma Wall",        "Accumulate 100 Diplomas",                "A+", "diplomas",       "",               100,             4),
    AchievementDef("combo_8",       "Flow State",          "Reach a combo of 8",                     "B+", "combo",          "",               8,               2),
    AchievementDef("faculty_3",     "Solid Team",          "Collect 3 Faculty Hire events",          "B+", "faculty_count",  "",               3,               2),
    AchievementDef("kp_10m",        "Ten Million Club",    "Earn 10 Million KP total",               "B+", "kp_total",       "",               10_000_000,      2),
    AchievementDef("kp_1b2",        "Billionaire Scholar", "Earn 1 Billion KP total (again!)",       "A",  "kp_total",       "",               1_000_000_000,   0),
    AchievementDef("prestige_3",    "Third Time's a Charm","Prestige 3 times",                       "A",  "prestige",       "",               3,               2),
    AchievementDef("prestige_7",    "Lucky Number",        "Prestige 7 times",                       "A",  "prestige",       "",               7,               3),
    AchievementDef("honor_3",       "Triple Honours",      "Earn 3 Honours",                         "A+", "honors",         "",               3,               3),
    AchievementDef("honor_10",      "Honour Hall",         "Earn 10 Honours",                        "S",  "honors",         "",               10,              4),

    # ── Hard (5–10 merit) ─────────────────────────────────────────────────────
    AchievementDef("prestige_15",   "Mid-Season Transfer", "Prestige 15 times",                      "S",  "prestige",       "",               15,              5),
    AchievementDef("prestige_20",   "Serial Graduate",     "Prestige 20 times",                      "S",  "prestige",       "",               20,              6),
    AchievementDef("kp_10t",        "Ten Trillion",        "Earn 10 Trillion KP total",              "S",  "kp_total",       "",               10_000_000_000_000, 6),
    AchievementDef("kp_100t",       "Hundred Trillion",    "Earn 100 Trillion KP total",             "S",  "kp_total",       "",               100_000_000_000_000, 7),
    AchievementDef("total_300",     "Mega Campus II",      "Own 300 buildings total",                "S",  "total_buildings","",               300,             5),
    AchievementDef("total_750",     "Titan Campus",        "Own 750 buildings total",                "S+", "total_buildings","",               750,             7),
    AchievementDef("bld_x200",      "Factory Floor",       "Own 200 of any one building",            "S",  "max_single_bld", "",               200,             6),
    AchievementDef("event_100",     "Century of Events",   "Collect 100 events",                     "S",  "events_collected","",              100,             5),
    AchievementDef("alumni_10",     "Distinguished Network","Earn 10 Alumni Points",                 "S",  "alumni_earned",  "",               10,              8),
    AchievementDef("endow_5",       "Five Pillars",        "Earn 5 Endowments",                      "S",  "endowments",     "",               5,               6),
    AchievementDef("endow_10",      "Foundation of Foundations","Earn 10 Endowments",                "S+", "endowments",     "",               10,              8),
    AchievementDef("dipl_250",      "Library Card Maxed",  "Accumulate 250 Diplomas",                "S",  "diplomas",       "",               250,             6),
    AchievementDef("dipl_500",      "Diploma Mountain",    "Accumulate 500 Diplomas",                "A+", "diplomas",       "",               500,             4),
    AchievementDef("dipl_1000",     "Diploma Dynasty",     "Accumulate 1,000 Diplomas",              "S",  "diplomas",       "",               1_000,           6),
    AchievementDef("research_25",   "Research Titan",      "Buy 25 Research Legacy grants",          "S+", "research_legacy","",              25,              8),
    AchievementDef("focus_100",     "Perpetual Motion",    "Use Focus abilities 100 times",          "S",  "focus_used",     "",               100,             6),

    # ── Very hard (10–15 merit) ───────────────────────────────────────────────
    AchievementDef("prestige_75",   "Forever Enrolled",    "Prestige 75 times",                      "S+", "prestige",       "",               75,              12),
    AchievementDef("kp_1q2",        "Beyond Reason",       "Earn 10 Quadrillion KP total",           "S+", "kp_total",       "",               10_000_000_000_000_000, 12),
    AchievementDef("total_1500",    "Continent of Learning","Own 1,500 buildings total",             "S+", "total_buildings","",               1_500,           12),
    AchievementDef("alumni_25",     "Legacy of Legends",   "Earn 25 Alumni Points",                  "S+", "alumni_earned",  "",               25,              12),
    AchievementDef("bld_x500",      "The Singularity",     "Own 500 of any one building",            "S+", "max_single_bld", "",               500,             12),
    AchievementDef("research_50",   "Infinite Scholar",    "Buy 50 Research Legacy grants",          "S+", "research_legacy","",              50,              12),
    AchievementDef("event_200",     "News Anchor",         "Collect 200 events",                     "S+", "events_collected","",              200,             10),
    AchievementDef("honor_20",      "Hall of Honour",      "Earn 20 Honours",                        "S+", "honors",         "",               20,              10),
    AchievementDef("endow_20",      "Eternal Endowment",   "Earn 20 Endowments",                     "S+", "endowments",     "",               20,              12),

    # ── Almost impossible (20–25 merit — still doable with enough dedication) ─
    AchievementDef("impossible_1",  "Centurion",           "Prestige 100 times",                     "S+", "prestige",       "",               100,             25),
    AchievementDef("impossible_2",  "Quadrillionaire",     "Earn 1 Quintillion KP total",            "S+", "kp_total",       "",               1_000_000_000_000_000_000, 25),
    AchievementDef("impossible_3",  "The Great Wall",      "Own 2,000 buildings total",              "S+", "total_buildings","",               2_000,           22),
    AchievementDef("impossible_4",  "Alumni Legend",       "Earn 50 Alumni Points",                  "S+", "alumni_earned",  "",               50,              25),
    AchievementDef("impossible_5",  "Obsessive Collector", "Own 1,000 of any one building",          "S+", "max_single_bld", "",               1_000,           22),
    AchievementDef("impossible_6",  "Research Immortal",   "Buy 100 Research Legacy grants",         "S+", "research_legacy","",              100,             25),
    AchievementDef("impossible_7",  "Event Deity",         "Collect 500 events",                     "S+", "events_collected","",              500,             20),
    AchievementDef("impossible_8",  "Click Deity",         "Click 1,000,000 times",                  "S+", "clicks",         "",               1_000_000,       22),
    AchievementDef("impossible_9",  "The Endowed One",     "Earn 50 Endowments",                     "S+", "endowments",     "",               50,              25),
    AchievementDef("impossible_10", "Multiversal Scholar", "Earn 100 Alumni Points",                 "S+", "alumni_earned",  "",               100,             25),

    # ── Quiz achievements ─────────────────────────────────────────────────────
    AchievementDef("quiz_basic",     "Pop Quiz",          "Earn a Basic reward from the quiz",               "C",  "quiz_tier",    "basic",      0, 1),
    AchievementDef("quiz_common",    "Class Act",         "Earn a Common reward from the quiz",              "B",  "quiz_tier",    "common",     0, 2),
    AchievementDef("quiz_rare",      "Academic Star",     "Earn a Rare reward from the quiz",                "B+", "quiz_tier",    "rare",       0, 3),
    AchievementDef("quiz_epic",      "Dean's List",       "Earn an Epic reward from the quiz",               "A",  "quiz_tier",    "epic",       0, 5),
    AchievementDef("quiz_legendary", "Nobel Candidate",   "Earn a Legendary reward from the quiz",           "A+", "quiz_tier",    "legendary",  0, 10),
    AchievementDef("quiz_mythic",    "Valedictorian",     "Earn the Mythic reward from the quiz",            "S",  "quiz_tier",    "mythic",     0, 25),
    AchievementDef("quiz_million",   "One in a Million",  "Like Bosson sang — all stats permanently +15%!",  "S+", "quiz_million", "",           0, 50),
]

# ── Building Synergies ────────────────────────────────────────────────────────
# Format: {building_name: [(source_building, bonus_per_source_count), ...]}

SYNERGIES: dict[str, list[tuple[str, float]]] = {
    "Classroom":           [("Library",          0.04)],
    "Science Lab":         [("Computer Lab",     0.08), ("Library",         0.03)],
    "Library":             [("University Wing",  0.12)],
    "Art Studio":          [("Sports Hall",      0.06), ("Computer Lab",    0.05)],
    "Sports Hall":         [("Classroom",        0.01)],
    "Computer Lab":        [("Science Lab",      0.05)],
    "University Wing":     [("Research Centre",  0.10)],
    "Innovation Hub":      [("Research Centre",  0.15)],
    "Space Academy":       [("Innovation Hub",   0.12)],
    "World Campus":        [("University Wing",  0.08), ("Space Academy",   0.10)],
    "Quantum Institute":   [("Research Centre",  0.05), ("Computer Lab",    0.03)],
    "Nexus of Knowledge":  [("Quantum Institute",0.20)],
}

# ── Building sacrifice requirements ──────────────────────────────────────────
# Each purchase of building N consumes this many of building N-1.
# Key = building being bought, value = (building consumed, count per purchase).
BUILDING_SACRIFICE: dict[str, tuple[str, int]] = {
    "Library":             ("Classroom",          10),
    "Science Lab":         ("Library",            10),
    "Computer Lab":        ("Science Lab",        10),
    "Sports Hall":         ("Computer Lab",       10),
    "Art Studio":          ("Sports Hall",        10),
    "University Wing":     ("Art Studio",         15),
    "Research Centre":     ("University Wing",    15),
    "Innovation Hub":      ("Research Centre",    20),
    "Space Academy":       ("Innovation Hub",     20),
    "World Campus":        ("Space Academy",      25),
    "Quantum Institute":   ("World Campus",       25),
    "Nexus of Knowledge":  ("Quantum Institute",  30),
}

# ── Diploma Shop (survives prestige, costs Diplomas) ─────────────────────────

DIPLOMA_UPGRADES: list[dict] = [
    {"id": "endowed_chair",  "name": "Endowed Chair",        "desc": "+5 base click power per click",     "cost": 3,  "effect": "click_base",    "value": 5.0},
    {"id": "alumni_network", "name": "Alumni Network",       "desc": "Offline earnings efficiency +25%",  "cost": 4,  "effect": "offline_eff",   "value": 0.25},
    {"id": "research_grant", "name": "Research Grant",       "desc": "All KP/s ×1.25 permanently",        "cost": 5,  "effect": "global_mult",   "value": 1.25},
    {"id": "campus_expand",  "name": "Campus Expansion",     "desc": "All building costs −15%",           "cost": 8,  "effect": "cost_discount", "value": 0.15},
    {"id": "click_mastery",  "name": "Click Mastery",        "desc": "Click power ×2 permanently",        "cost": 10, "effect": "click_mult",    "value": 2.0},
    {"id": "distinguished",  "name": "Distinguished Faculty","desc": "All KP/s ×1.5 permanently",         "cost": 15, "effect": "global_mult",   "value": 1.5},
    {"id": "ivy_status",     "name": "Ivy League Status",    "desc": "All building costs −25% extra",     "cost": 20, "effect": "cost_discount", "value": 0.25},
    {"id": "nobel_legacy",   "name": "Nobel Legacy",         "desc": "All KP/s ×2 permanently",          "cost": 25, "effect": "global_mult",   "value": 2.0},
    {"id": "golden_campus",  "name": "Golden Campus",        "desc": "Click power ×3 permanently",        "cost": 30, "effect": "click_mult",    "value": 3.0},
    {"id": "grand_endowment","name": "Grand Endowment",      "desc": "All KP/s ×3 permanently",           "cost": 50, "effect": "global_mult",   "value": 3.0},
    {"id": "extended_leave", "name": "Extended Leave", "desc": "Offline earnings cap +12 hours (total 20 h)", "cost": 8, "effect": "offline_cap_bonus", "value": 12.0},
    {"id": "auto_lecture_1", "name": "Auto-Lecturer I",   "desc": "Lectures automatically — 0.5 clicks per second.",           "cost": 12, "effect": "auto_click_rate", "value": 0.5},
    {"id": "auto_lecture_2", "name": "Auto-Lecturer II",  "desc": "More automation — brings total to 2 auto-clicks per second.","cost": 28, "effect": "auto_click_rate", "value": 1.5},
    {"id": "auto_lecture_3", "name": "Auto-Lecturer III", "desc": "Full automation — 8 auto-clicks per second total.",           "cost": 60, "effect": "auto_click_rate", "value": 6.0},
]

# ── Honor Shop (survives everything, costs Honors) ────────────────────────────

HONOR_UPGRADES: list[dict] = [
    {"id": "honor_lecture",  "name": "Honorary Lecture",     "desc": "All KP/s ×1.10 permanently",        "cost": 1,  "effect": "global_mult",   "value": 1.10},
    {"id": "honor_fellow",   "name": "Research Fellowship",  "desc": "Click power ×1.5 permanently",      "cost": 2,  "effect": "click_mult",    "value": 1.5},
    {"id": "honor_merit",    "name": "Merit Scholarship",    "desc": "+1 Merit per achievement",           "cost": 2,  "effect": "merit_bonus",   "value": 1.0},
    {"id": "honor_offline",  "name": "Extended Study Hall",  "desc": "Offline efficiency +15%",           "cost": 3,  "effect": "offline_eff",   "value": 0.15},
    {"id": "honor_clickb",   "name": "Honours Desk",         "desc": "+10 base click power",              "cost": 3,  "effect": "click_base",    "value": 10.0},
    {"id": "honor_cost",     "name": "Honours Discount",     "desc": "All building costs −10%",           "cost": 4,  "effect": "cost_discount", "value": 0.10},
    {"id": "honor_kps",      "name": "Academic Prestige",    "desc": "All KP/s ×1.25 permanently",        "cost": 5,  "effect": "global_mult",   "value": 1.25},
    {"id": "honor_synergy",  "name": "Synergy Amplifier",    "desc": "All synergy bonuses ×1.5",          "cost": 6,  "effect": "synergy_amp",   "value": 0.5},
    {"id": "honor_diplomas", "name": "Diploma Surplus",      "desc": "All KP/s ×1.5 permanently",         "cost": 8,  "effect": "global_mult",   "value": 1.5},
    {"id": "honor_apex",     "name": "Apex Scholar",         "desc": "All KP/s ×2 permanently",           "cost": 12, "effect": "global_mult",   "value": 2.0},
]

# ── Endowment Shop (permanent forever, costs Endowments) ─────────────────────

ENDOW_UPGRADES: list[dict] = [
    {"id": "endow_found",    "name": "Foundation Grant",     "desc": "All KP/s ×1.25 permanently",        "cost": 1,  "effect": "global_mult",   "value": 1.25},
    {"id": "endow_click",    "name": "Endowed Clicks",       "desc": "Click power ×2 permanently",        "cost": 1,  "effect": "click_mult",    "value": 2.0},
    {"id": "endow_campus",   "name": "Endowed Campus",       "desc": "All building costs −15%",           "cost": 2,  "effect": "cost_discount", "value": 0.15},
    {"id": "endow_faculty",  "name": "Distinguished Faculty II","desc": "All KP/s ×2 permanently",        "cost": 3,  "effect": "global_mult",   "value": 2.0},
    {"id": "endow_study",    "name": "Endowment Study Cap",  "desc": "Offline efficiency +25%",           "cost": 3,  "effect": "offline_eff",   "value": 0.25},
    {"id": "endow_legacy",   "name": "Eternal Legacy",       "desc": "All KP/s ×3 permanently",           "cost": 5,  "effect": "global_mult",   "value": 3.0},
]

# ── Alumni Network Shop (costs Alumni Points — the 4th prestige currency) ─────

ALUMNI_UPGRADES: list[dict] = [
    {"id": "alum_kps1",   "name": "Pioneer Legacy",      "desc": "All KPS ×1.5 permanently",     "cost": 1, "effect": "global_mult",   "value": 1.5},
    {"id": "alum_click1", "name": "Tenure Track",         "desc": "Click power ×2 permanently",   "cost": 1, "effect": "click_mult",    "value": 2.0},
    {"id": "alum_kps2",   "name": "Research Network",     "desc": "All KPS ×2 permanently",       "cost": 2, "effect": "global_mult",   "value": 2.0},
    {"id": "alum_cost",   "name": "Alumni Discount",      "desc": "All building costs −20%",      "cost": 2, "effect": "cost_discount", "value": 0.20},
    {"id": "alum_kps3",   "name": "Century Endowment",    "desc": "All KPS ×3 permanently",       "cost": 4, "effect": "global_mult",   "value": 3.0},
    {"id": "alum_click2", "name": "Distinguished Alumni", "desc": "Click power ×4 permanently",   "cost": 4, "effect": "click_mult",    "value": 4.0},
    {"id": "alum_kps4",   "name": "Infinite Knowledge",   "desc": "All KPS ×5 permanently",       "cost": 6, "effect": "global_mult",   "value": 5.0},
]

# ── Historical Scholars (purchasable with Honors, permanent bonuses) ──────────

SCHOLARS: list[dict] = [
    {"id": "socrates",   "name": "Socrates",          "era": "470–399 BC",
     "desc": "Father of the Socratic method — questions over answers.",
     "bonus": "Classrooms +20% KPS",
     "cost": 2, "effect": "building_bonus", "target": "Classroom",       "value": 0.20},
    {"id": "plato",      "name": "Plato",              "era": "428–348 BC",
     "desc": "Founded the Academy — the first Western institution of higher learning.",
     "bonus": "Libraries +20% KPS",
     "cost": 2, "effect": "building_bonus", "target": "Library",          "value": 0.20},
    {"id": "confucius",  "name": "Confucius",           "era": "551–479 BC",
     "desc": "Teacher of ethics, wisdom, and lifelong learning.",
     "bonus": "+10% global KPS",
     "cost": 3, "effect": "global_kps",     "target": "",                 "value": 0.10},
    {"id": "archimedes", "name": "Archimedes",          "era": "287–212 BC",
     "desc": "Mathematician and engineer — Eureka!",
     "bonus": "Science Labs +25% KPS",
     "cost": 3, "effect": "building_bonus", "target": "Science Lab",      "value": 0.25},
    {"id": "newton",     "name": "Isaac Newton",        "era": "1643–1727",
     "desc": "Laws of motion, gravity, and calculus. Standing on shoulders of giants.",
     "bonus": "Science Labs +35% KPS",
     "cost": 4, "effect": "building_bonus", "target": "Science Lab",      "value": 0.35},
    {"id": "tesla",      "name": "Nikola Tesla",        "era": "1856–1943",
     "desc": "Pioneer of alternating current and wireless technology.",
     "bonus": "Computer Labs +30% KPS",
     "cost": 4, "effect": "building_bonus", "target": "Computer Lab",     "value": 0.30},
    {"id": "dewey",      "name": "John Dewey",          "era": "1859–1952",
     "desc": "'Learning by doing.' Father of progressive education.",
     "bonus": "University Wings +30% KPS",
     "cost": 5, "effect": "building_bonus", "target": "University Wing",  "value": 0.30},
    {"id": "lovelace",   "name": "Ada Lovelace",        "era": "1815–1852",
     "desc": "World's first computer programmer — wrote algorithms for Babbage's engine.",
     "bonus": "Computer Labs +40% KPS",
     "cost": 5, "effect": "building_bonus", "target": "Computer Lab",     "value": 0.40},
    {"id": "curie",      "name": "Marie Curie",         "era": "1867–1934",
     "desc": "Two Nobel Prizes. Discovered polonium and radium.",
     "bonus": "Research Centres +35% KPS",
     "cost": 5, "effect": "building_bonus", "target": "Research Centre",  "value": 0.35},
    {"id": "davinci",    "name": "Leonardo da Vinci",   "era": "1452–1519",
     "desc": "The Renaissance ideal — art, science, and engineering as one.",
     "bonus": "Art Studios +35% KPS",
     "cost": 5, "effect": "building_bonus", "target": "Art Studio",       "value": 0.35},
    {"id": "einstein",   "name": "Albert Einstein",     "era": "1879–1955",
     "desc": "Theory of relativity — E=mc². Redefined space, time, and gravity.",
     "bonus": "+20% global KPS",
     "cost": 6, "effect": "global_kps",     "target": "",                 "value": 0.20},
    {"id": "aristotle",  "name": "Aristotle",           "era": "384–322 BC",
     "desc": "Tutor of Alexander the Great. Wrote on logic, ethics, science, and art.",
     "bonus": "+15% global KPS",
     "cost": 6, "effect": "global_kps",     "target": "",                 "value": 0.15},
]

# ── Story Chapters (12 total) ─────────────────────────────────────────────────

STORY: list[dict] = [
    {"id": "ch1", "title": "The Empty Lot",
     "text": (
         "You stand before an empty field on the edge of town.\n"
         "The local authority has handed you a budget and a dream:\n"
         "build an educational institution worthy of this community.\n\n"
         "It won't be easy. It will never be finished.\n"
         "But every great school starts with a single desk."
     ),
     "check": "start"},
    {"id": "ch2", "title": "First Day of Class",
     "text": (
         "The smell of fresh paint. Squeaky chairs. A nervous teacher.\n"
         "Ten students file in — eyes bright, pencils ready.\n\n"
         "You watch through the window and feel something unexpected:\n"
         "pride. This is where futures are made."
     ),
     "check": "building", "target": "Classroom", "value": 1},
    {"id": "ch3", "title": "Word Spreads",
     "text": (
         "Parents talk at the school gates.\n"
         "'Have you heard about the new school? A real one.'\n\n"
         "Applications are flooding in. The waiting list grows daily.\n"
         "You need more space — and more Knowledge Points."
     ),
     "check": "kp_total", "value": 500},
    {"id": "ch4", "title": "An Institution",
     "text": (
         "The library opens its doors for the first time.\n"
         "Scholars, dreamers, and students who just need somewhere quiet\n"
         "all find their way here.\n\n"
         "Your school has become something the town believes in."
     ),
     "check": "building", "target": "Library", "value": 1},
    {"id": "ch5", "title": "The Golden Age",
     "text": (
         "Science labs hum. Computers glow through late-night windows.\n"
         "Your students are solving problems the world hasn't asked yet.\n\n"
         "A journalist calls it 'the most ambitious school in the region.'\n"
         "You just call it Tuesday."
     ),
     "check": "kp_total", "value": 50_000},
    {"id": "ch6", "title": "Graduation Day",
     "text": (
         "Caps fly into the air. A roar from the crowd.\n"
         "Your first graduating class steps into the world,\n"
         "carrying everything you built with them.\n\n"
         "And so — we begin again. Smarter. Stronger. Better."
     ),
     "check": "prestige", "value": 1},
    {"id": "ch7", "title": "The Legacy Continues",
     "text": (
         "Alumni return with stories of breakthroughs, discoveries, success.\n"
         "They want to give back — to be part of what you've built.\n\n"
         "With every diploma earned, the empire grows.\n"
         "The cycle of knowledge never stops."
     ),
     "check": "prestige", "value": 2},
    {"id": "ch8", "title": "The First Honour",
     "text": (
         "A ceremony unlike any before it.\n"
         "The chancellor places a sash across your shoulders.\n"
         "Honours Graduate.\n\n"
         "Your peers applaud — the sound echoes across the campus\n"
         "you built with nothing but a field and determination.\n"
         "This is only the beginning of a new chapter."
     ),
     "check": "honors", "value": 1},
    {"id": "ch9", "title": "Into the Cosmos",
     "text": (
         "The Space Academy launch ceremony is breathtaking.\n"
         "Students in training suits wave to the cameras.\n"
         "Your school is now studying the universe itself.\n\n"
         "The official who handed you that first budget\n"
         "looks up at the sky, speechless."
     ),
     "check": "building", "target": "Space Academy", "value": 1},
    {"id": "ch10", "title": "Among the Elite",
     "text": (
         "One trillion Knowledge Points.\n"
         "A number so vast it stops meaning anything —\n"
         "until you look at the faces of those you've taught.\n\n"
         "Doctors. Engineers. Artists. Parents. Leaders.\n"
         "You didn't just build a school.\n"
         "You built a world."
     ),
     "check": "kp_total", "value": 1_000_000_000_000},
    {"id": "ch11", "title": "The Endowment",
     "text": (
         "The first endowment arrives — a transformative gift\n"
         "from a network of your graduates, spanning every continent.\n"
         "They don't call it charity. They call it paying it forward.\n\n"
         "Edu Empire is now permanent in a way\n"
         "no building ever could be."
     ),
     "check": "endowments", "value": 1},
    {"id": "ch12", "title": "The Nexus Awakens",
     "text": (
         "The Nexus of Knowledge opens its doors.\n"
         "It is simultaneously a library, a research centre,\n"
         "a lecture hall, and a portal to every piece of\n"
         "human understanding ever recorded.\n\n"
         "Someone asks: 'Are you finished?'\n"
         "You laugh. You will never be finished."
     ),
     "check": "building", "target": "Nexus of Knowledge", "value": 1},
    {"id": "ch13", "title": "The Alumni Network",
     "text": (
         "Thousands of graduates. Hundreds of careers. Dozens of nations.\n"
         "They all share one thing: they were shaped here.\n\n"
         "The Alumni Network is more than a list of names —\n"
         "it is a living web of influence that reaches back\n"
         "to lift every student who comes after.\n\n"
         "Your legacy now outlives any single school."
     ),
     "check": "alumni", "value": 1},
    {"id": "ch14", "title": "A Scholar Arrives",
     "text": (
         "Word travels fast in academic circles.\n"
         "A figure whose work you studied years ago\n"
         "walks through your doors — not as a visitor,\n"
         "but as a colleague.\n\n"
         "They bring more than knowledge.\n"
         "They bring credibility, history, and wonder.\n"
         "Your students will remember this year."
     ),
     "check": "scholars_count", "value": 1},
    {"id": "ch15", "title": "The Seasons Turn",
     "text": (
         "You've watched this place change with the light.\n"
         "Autumn's first frosts, the quiet of winter exams,\n"
         "spring's restlessness, summer's long evenings.\n\n"
         "A full year of learning. A full year of growth.\n"
         "And yet somehow it feels like you're only just beginning."
     ),
     "check": "full_year", "value": 1},
    {"id": "ch16", "title": "A Thousand of One",
     "text": (
         "You pause and look at the numbers.\n"
         "One thousand. Of a single type of building.\n\n"
         "There is no word for what this campus has become.\n"
         "A city of learning. A monument to persistence.\n"
         "Each room the same, yet every lesson different.\n\n"
         "The students don't notice the scale.\n"
         "They just know this is where they want to be."
     ),
     "check": "star_hit", "value": 1},
]

# ── Random Events (14 total, with rarity weighting) ──────────────────────────
# Rarity: common=60%, uncommon=30%, rare=10% (weighted selection)

EVENTS: list[dict] = [
    # Common (original)
    {"id": "fundraiser",    "name": "School Fundraiser!",
     "desc": "Local businesses donated — earn 5 minutes of KP instantly.",
     "type": "kp_bonus",    "value_mult": 300,  "rarity": "common"},
    {"id": "quiz",          "name": "Pop Quiz Craze!",
     "desc": "Friendly competition spikes engagement. Click power ×5 for 30s!",
     "type": "click_boost", "value": 5.0, "duration": 30, "rarity": "common"},
    {"id": "science_fair",  "name": "Science Fair Day!",
     "desc": "Inventions everywhere. Earn 7.5 minutes of KP now!",
     "type": "kp_bonus",    "value_mult": 450,  "rarity": "common"},
    {"id": "time_capsule",  "name": "Time Capsule Opened!",
     "desc": "Students find old records. Earn 8 minutes of KP!",
     "type": "kp_bonus",    "value_mult": 480,  "rarity": "common"},
    # Uncommon
    {"id": "speaker",       "name": "Inspiring Guest Speaker!",
     "desc": "A Nobel laureate is visiting. KP/s ×2 for 30 seconds!",
     "type": "kps_boost",   "value": 2.0, "duration": 30, "rarity": "uncommon"},
    {"id": "grant",         "name": "Education Grant Awarded!",
     "desc": "The government recognises your excellence. +5 Merit Points!",
     "type": "merit_bonus", "value": 5,   "rarity": "uncommon"},
    {"id": "inspection",    "name": "Inspection: Outstanding!",
     "desc": "Inspectors were blown away. KP/s ×3 for 20 seconds!",
     "type": "kps_boost",   "value": 3.0, "duration": 20, "rarity": "uncommon"},
    {"id": "hackathon",     "name": "Coding Hackathon!",
     "desc": "Students are building amazing things. KP/s ×2.5 for 45s!",
     "type": "kps_boost",   "value": 2.5, "duration": 45, "rarity": "uncommon"},
    {"id": "scholarships",  "name": "Scholarship Wave!",
     "desc": "National recognition brings funding. +7 Merit Points!",
     "type": "merit_bonus", "value": 7,   "rarity": "uncommon"},
    {"id": "research_pub",  "name": "Research Published!",
     "desc": "A breakthrough paper puts you on the map. KP/s ×4 for 25s!",
     "type": "kps_boost",   "value": 4.0, "duration": 25, "rarity": "uncommon"},
    # Rare — Faculty hire (target building filled dynamically at spawn)
    {"id": "faculty",       "name": "Faculty Hire!",
     "desc": "A renowned educator joins your staff permanently!",
     "type": "faculty",     "value": 0.02, "rarity": "rare"},
    # Rare
    {"id": "viral",         "name": "School Goes Viral!",
     "desc": "A student video reached millions. Earn 10 minutes of KP now!",
     "type": "kp_bonus",    "value_mult": 600,  "rarity": "rare"},
    {"id": "alumni",        "name": "Alumni Donation Drive!",
     "desc": "Former students give back generously. Earn 15 minutes of KP!",
     "type": "kp_bonus",    "value_mult": 900,  "rarity": "rare"},
    {"id": "benefactor",    "name": "Mystery Benefactor!",
     "desc": "An anonymous donor writes a massive cheque. Earn 30 min of KP!",
     "type": "kp_bonus",    "value_mult": 1800, "rarity": "rare"},
    {"id": "olympiad",      "name": "Academic Olympiad!",
     "desc": "Your students sweep every category. Click power ×20 for 30s!",
     "type": "click_boost", "value": 20.0, "duration": 30, "rarity": "rare"},
    # New — scholar / alumni themed
    {"id": "star_student",  "name": "Star Student!",
     "desc": "An exceptional pupil inspires the whole school. Click ×6 for 30s!",
     "type": "click_boost", "value": 6.0,  "duration": 30, "rarity": "common"},
    {"id": "scholar_visit", "name": "Scholar in Residence!",
     "desc": "A visiting scholar runs a lecture series. KP/s ×3 for 40s!",
     "type": "kps_boost",   "value": 3.0,  "duration": 40, "rarity": "uncommon"},
    {"id": "research_break","name": "Research Breakthrough!",
     "desc": "Your team makes a pivotal discovery — earn 10 minutes of KP!",
     "type": "kp_bonus",    "value_mult": 600, "rarity": "uncommon"},
    {"id": "national_medal","name": "National Medal!",
     "desc": "The government recognises your institution. +12 Merit Points!",
     "type": "merit_bonus", "value": 12,   "rarity": "rare"},
    {"id": "world_record",  "name": "World Education Record!",
     "desc": "Your school makes global headlines. KP/s ×5 for 30 seconds!",
     "type": "kps_boost",   "value": 5.0,  "duration": 30, "rarity": "rare"},
    {"id": "staff_strike",  "name": "Staff on Strike!",
     "desc": "Teachers, janitors, and cafeteria staff walk out! All idle KP/s −75% for 60 seconds. Pay 5 Merit to resolve early.",
     "type": "strike",      "duration": 60, "rarity": "uncommon"},
    {"id": "inspection_challenge", "name": "Ofsted Inspection!",
     "desc": "The inspector is watching! Click the Study button 30 times in 20 seconds to earn a bonus!",
     "type": "inspection_challenge", "duration": 20.0, "clicks_needed": 30, "rarity": "uncommon"},
]

# Rarity weights for weighted random selection
EVENT_RARITY_WEIGHTS: dict[str, int] = {"common": 60, "uncommon": 30, "rare": 10}

# ── Multiverse Shop (purchased with Cosmic Wisdom) ────────────────────────────

CW_SHOP: list[dict] = [
    # Zone-wide KPS multipliers
    {"id": "cw_synergy_1", "name": "Multiversal Synergy I",
     "cost": 5,  "desc": "+25% KP/s in all zones and Zone 1.",
     "effect": "zone_global_mult", "value": 1.25, "req": None},
    {"id": "cw_synergy_2", "name": "Multiversal Synergy II",
     "cost": 15, "desc": "+75% KP/s in all zones (stacks).",
     "effect": "zone_global_mult", "value": 1.75, "req": "cw_synergy_1"},
    {"id": "cw_synergy_3", "name": "Multiversal Synergy III",
     "cost": 40, "desc": "All zones and Zone 1 produce ×3 KP/s.",
     "effect": "zone_global_mult", "value": 3.00, "req": "cw_synergy_2"},
    # Zone 1 diploma bonus
    {"id": "cw_diploma_1", "name": "Academic Resonance I",
     "cost": 10, "desc": "+2 Diplomas per prestige in Zone 1.",
     "effect": "zone1_diploma_bonus", "value": 2, "req": None},
    {"id": "cw_diploma_2", "name": "Academic Resonance II",
     "cost": 25, "desc": "+5 more Diplomas per prestige (total +7).",
     "effect": "zone1_diploma_bonus", "value": 5, "req": "cw_diploma_1"},
    # Zone 1 click power
    {"id": "cw_click_1",   "name": "Cosmic Click I",
     "cost": 8,  "desc": "×2 click power in Zone 1.",
     "effect": "zone1_click_mult", "value": 2.0, "req": None},
    {"id": "cw_click_2",   "name": "Cosmic Click II",
     "cost": 20, "desc": "×4 click power in Zone 1 (total ×8 with I).",
     "effect": "zone1_click_mult", "value": 4.0, "req": "cw_click_1"},
    # Cosmetic unlocks
    {"id": "cw_cosmetic_night",  "name": "Night Campus",
     "cost": 3,  "desc": "Unlock Night sky theme for the campus mini-view.",
     "effect": "cosmetic", "value": "night", "req": None},
    {"id": "cw_cosmetic_sunset", "name": "Golden Hour",
     "cost": 3,  "desc": "Unlock Sunset theme for the campus mini-view.",
     "effect": "cosmetic", "value": "sunset", "req": None},
    {"id": "cw_cosmetic_storm",  "name": "Stormy Academy",
     "cost": 5,  "desc": "Unlock Stormy weather theme for the campus mini-view.",
     "effect": "cosmetic", "value": "storm", "req": None},
]

# ── Educational Quiz Questions ─────────────────────────────────────────────────

QUIZ_QUESTIONS: list[dict] = [
    # Math
    {"type": "math",     "q": "What is 7 × 8?",                            "a": "56",            "choices": ["42", "54", "56", "63"]},
    {"type": "math",     "q": "What is √144?",                             "a": "12",            "choices": ["10", "12", "14", "16"]},
    {"type": "math",     "q": "What is 15% of 200?",                       "a": "30",            "choices": ["25", "30", "35", "40"]},
    {"type": "math",     "q": "What is 2 to the power of 10?",             "a": "1024",          "choices": ["512", "1000", "1024", "2048"]},
    {"type": "math",     "q": "Sum of angles in a triangle?",              "a": "180°",          "choices": ["90°", "180°", "270°", "360°"]},
    {"type": "math",     "q": "What is 0.25 as a fraction?",               "a": "1/4",           "choices": ["1/2", "1/3", "1/4", "1/5"]},
    {"type": "math",     "q": "What is 13 × 13?",                          "a": "169",           "choices": ["156", "163", "169", "172"]},
    {"type": "math",     "q": "Value of π to 2 decimal places?",           "a": "3.14",          "choices": ["3.12", "3.14", "3.16", "3.18"]},
    {"type": "math",     "q": "Right triangle sides 3, 4, and ?",          "a": "5",             "choices": ["4", "5", "6", "7"]},
    {"type": "math",     "q": "What is 1000 ÷ 8?",                         "a": "125",           "choices": ["100", "112", "125", "150"]},
    # Spelling
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "necessary",    "choices": ["neccessary", "necessary", "necesary", "neccesary"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "occurrence",   "choices": ["occurence", "occurrence", "ocurrence", "occurrance"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "accommodate",  "choices": ["acommodate", "accommodate", "accomodate", "accommadate"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "conscience",   "choices": ["concience", "concsience", "conscience", "conshience"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "separate",     "choices": ["seperate", "seprate", "separate", "sepperate"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "privilege",    "choices": ["priviledge", "privilage", "privilege", "privilège"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "millennium",   "choices": ["millenium", "millennium", "millennuim", "milenium"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "embarrass",    "choices": ["embaras", "embarass", "embarrass", "embarrase"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "lieutenant",   "choices": ["leutenant", "lieutenent", "lieutenant", "leuitenant"]},
    {"type": "spelling", "q": "Which is spelled correctly?",               "a": "Mediterranean","choices": ["Mediteranean", "Mediterraneon", "Mediterranean", "Mediterrenean"]},
    # History
    {"type": "history",  "q": "What year did World War II end?",           "a": "1945",          "choices": ["1942", "1943", "1945", "1947"]},
    {"type": "history",  "q": "First person to walk on the Moon?",         "a": "Neil Armstrong","choices": ["Buzz Aldrin", "Neil Armstrong", "Yuri Gagarin", "Alan Shepard"]},
    {"type": "history",  "q": "What year did the Berlin Wall fall?",       "a": "1989",          "choices": ["1985", "1987", "1989", "1991"]},
    {"type": "history",  "q": "What year did World War I begin?",          "a": "1914",          "choices": ["1912", "1914", "1916", "1918"]},
    {"type": "history",  "q": "What year did Columbus reach the Americas?","a": "1492",          "choices": ["1488", "1490", "1492", "1495"]},
    {"type": "history",  "q": "What ship sank in the North Atlantic 1912?","a": "Titanic",       "choices": ["Lusitania", "Titanic", "Britannic", "Olympic"]},
    {"type": "history",  "q": "What year did the French Revolution begin?","a": "1789",          "choices": ["1776", "1783", "1789", "1799"]},
    {"type": "history",  "q": "First President of the United States?",     "a": "Washington",    "choices": ["Adams", "Jefferson", "Washington", "Franklin"]},
    {"type": "history",  "q": "What year did the first human reach space?","a": "1961",          "choices": ["1957", "1959", "1961", "1963"]},
    {"type": "history",  "q": "Who proposed the theory of relativity?",    "a": "Einstein",      "choices": ["Newton", "Darwin", "Einstein", "Hawking"]},
]

QUIZ_REWARDS: dict[str, dict] = {
    "basic":     {"name": "Basic",     "color": (160, 160, 170), "weight": 40,
                  "desc": "+100% KP/s for 60 seconds",           "type": "kps_boost",    "value": 2.0,  "duration": 60.0},
    "common":    {"name": "Common",    "color": (80, 180, 80),   "weight": 30,
                  "desc": "×3 click power for 90 seconds",       "type": "click_boost",  "value": 3.0,  "duration": 90.0},
    "rare":      {"name": "Rare",      "color": (60, 120, 220),  "weight": 15,
                  "desc": "Permanent +10% KP/s (stacks)",        "type": "perm_kps",     "value": 0.10, "duration": 0},
    "epic":      {"name": "Epic",      "color": (160, 60, 220),  "weight": 9,
                  "desc": "+2 Diplomas on next prestige",        "type": "perm_diploma", "value": 2,    "duration": 0},
    "legendary": {"name": "Legendary", "color": (220, 140, 20),  "weight": 5,
                  "desc": "Permanent +25% KP/s (stacks)",        "type": "perm_kps",     "value": 0.25, "duration": 0},
    "mythic":    {"name": "Mythic",    "color": (255, 215, 0),   "weight": 1,
                  "desc": "Prestige without losing progress!",   "type": "free_prestige","value": 0,    "duration": 0},
}

# ── Campus Cosmetic Themes ────────────────────────────────────────────────────
# sky = (R,G,B) overlay tint applied over zone 1's default sky
# ground = (R,G,B) override for the ground rectangle colour
# tint_alpha = 0–180, strength of the sky overlay (0 = no tint)

COSMETIC_THEMES: list[dict] = [
    {"id": "classic", "name": "Classic Day",    "tint": None,           "tint_alpha": 0,   "ground": (138, 178, 112), "always_unlocked": True},
    {"id": "night",   "name": "Night Campus",   "tint": (5, 5, 40),     "tint_alpha": 160, "ground": (20,  55,  20),  "cw_req": "cw_cosmetic_night"},
    {"id": "sunset",  "name": "Golden Hour",    "tint": (220, 80, 10),  "tint_alpha": 100, "ground": (90,  65,  35),  "cw_req": "cw_cosmetic_sunset"},
    {"id": "storm",   "name": "Stormy Academy", "tint": (60, 65, 95),   "tint_alpha": 120, "ground": (55,  80,  45),  "cw_req": "cw_cosmetic_storm"},
]

# ── Dynamic News Templates ────────────────────────────────────────────────────
# {school} → school name   {name} → achievement / building name

DYNAMIC_NEWS_BUILDING: dict[str, list[str]] = {
    "Classroom": [
        "{school} opens its first classroom — ten eager students already enrolled!",
        "Education arrives as {school} opens its very first classroom today.",
        "Breaking: {school} officially opens for students. Local families cheer.",
    ],
    "Library": [
        "{school} opens a brand-new library — bookworms lined up before dawn.",
        "A hush falls over {school}'s new library as the first readers arrive.",
        "Pages, peace, and possibility: {school} unveils its first library.",
    ],
    "Science Lab": [
        "Experiments begin! {school}'s new Science Lab is officially open.",
        "{school} launches its Science Lab — students are buzzing with excitement.",
        "Beakers, bunsen burners, breakthroughs: {school} opens its Science Lab.",
    ],
    "Computer Lab": [
        "{school} goes digital with a brand-new Computer Lab — fast internet included.",
        "Screens glow at {school}'s new Computer Lab — the future is now.",
        "Technology arrives at {school} as its Computer Lab opens to students.",
    ],
    "Sports Hall": [
        "{school} breaks ground on a Sports Hall — PE lessons just got exciting.",
        "Whistles blow and trainers squeak: {school}'s Sports Hall is now open.",
        "A cheer echoes across campus as {school} opens its brand-new Sports Hall.",
    ],
    "Art Studio": [
        "Paint, clay, and creativity: {school}'s Art Studio opens its doors.",
        "{school} unveils a stunning new Art Studio — commissions already flooding in.",
        "The walls of {school}'s new Art Studio are already covered in masterpieces.",
    ],
    "University Wing": [
        "{school} reaches new heights with the opening of its University Wing.",
        "Higher education has arrived: {school} opens a full University Wing.",
        "{school}'s University Wing opens — the waiting list is already full.",
    ],
    "Research Centre": [
        "Groundbreaking research is underway at {school}'s new Research Centre.",
        "{school} Research Centre opens — first papers expected within the month.",
        "Scientists flock to {school} after its Research Centre opens today.",
    ],
    "Innovation Hub": [
        "{school}'s Innovation Hub opens — three start-ups already in residence.",
        "Ideas collide at {school}'s new Innovation Hub. Something big is coming.",
        "The future is being invented right now inside {school}'s Innovation Hub.",
    ],
    "Space Academy": [
        "{school} reaches for the stars with the opening of its Space Academy.",
        "T-minus zero: {school}'s Space Academy launches its first cohort.",
        "Astronauts of tomorrow begin training today at {school}'s Space Academy.",
    ],
    "World Campus": [
        "{school}'s World Campus is open — students joining from 47 countries.",
        "Knowledge without borders: {school} launches its global World Campus.",
        "{school} World Campus opens — live-streamed to six continents simultaneously.",
    ],
    "Quantum Institute": [
        "{school} enters a new dimension with the opening of its Quantum Institute.",
        "Observers collapse the wave function at {school}'s Quantum Institute opening.",
        "The Quantum Institute at {school} is open — reality may never be the same.",
    ],
    "Nexus of Knowledge": [
        "{school}'s Nexus of Knowledge opens — described as 'the greatest library ever built'.",
        "All of human understanding, in one place: {school}'s Nexus of Knowledge.",
        "Crowds gather in awe as {school} unveils its legendary Nexus of Knowledge.",
    ],
}

DYNAMIC_NEWS_ACHIEVEMENT: list[str] = [
    "{school} awarded the '{name}' distinction — staff and students celebrate.",
    "Inspectors confirm: '{name}' awarded to {school}. A proud day for the campus.",
    "{school} earns '{name}' — the local community turns out for the announcement.",
    "The '{name}' award arrives at {school}. The principal is reportedly speechless.",
    "Official recognition for {school}: '{name}' achieved after remarkable progress.",
    "Word spreads fast — {school} has just unlocked '{name}'. Remarkable.",
]

DYNAMIC_NEWS_PRESTIGE: list[str] = [
    "Graduation day at {school} — caps in the air and tears of pride.",
    "{school} celebrates another graduating class. Diplomas handed out across the hall.",
    "The class of this year bids farewell to {school} — heading out to change the world.",
    "Record numbers graduate at {school} as the ceremony draws a packed crowd.",
    "Alumni of {school} return to cheer on this year's graduating class. Magnificent scenes.",
    "{school} graduation ceremony declared 'the best yet' by the outgoing class.",
]

DYNAMIC_NEWS_MILESTONE: dict[str, list[str]] = {
    "100": [
        "{school} — already generating serious Knowledge Points. Watch this space.",
    ],
    "1000": [
        "{school} hits 1,000 Knowledge Points. 'Only the beginning,' says the principal.",
        "One thousand KP and counting — {school} is just getting started.",
    ],
    "10000": [
        "{school} surpasses 10,000 Knowledge Points — the local board calls it 'exceptional'.",
        "Ten thousand Knowledge Points at {school}. Students celebrate in the halls.",
    ],
    "100000": [
        "{school} crosses 100,000 KP — regional press starts paying attention.",
        "One hundred thousand Knowledge Points! {school} named 'School of the Season'.",
    ],
    "1000000": [
        "One million Knowledge Points at {school} — a national landmark moment.",
        "{school} reaches 1 Million KP. The Mayor personally calls to congratulate.",
        "The million-KP mark! Fireworks spotted above {school}'s main building.",
    ],
    "10000000": [
        "{school} soars past 10 Million KP. International observers take notice.",
        "Ten million Knowledge Points at {school}. The story is going global.",
    ],
    "100000000": [
        "{school} earns 100 Million KP — documentary crew spotted on campus.",
        "A hundred million KP! {school} is now the talk of the education world.",
    ],
    "1000000000": [
        "{school} hits 1 Billion KP — government officials are asking questions.",
        "Billion-KP club: {school} joins an elite group of educational institutions.",
    ],
    "1000000000000": [
        "{school} earns 1 Trillion KP. Scientists can't explain it. Students just smile.",
        "A trillion Knowledge Points! {school} is now simply beyond comprehension.",
    ],
}

# ── News Ticker ───────────────────────────────────────────────────────────────

NEWS: list[str] = [
    "Principal announces record-breaking enrolment numbers this term!",
    "Library card renewals now open — ask at the front desk.",
    "Science fair entries due by end of term. Good luck!",
    "Reminder: the cafeteria serves hot meals until 2pm.",
    "Computer Lab is open for enrolled students after hours.",
    "Congratulations to this term's honour roll recipients!",
    "School play auditions begin Monday — all students welcome.",
    "New textbooks have arrived for Advanced Mathematics.",
    "Sports Hall now open on weekends. Bring your student ID.",
    "Art Studio competition: submit entries before the deadline.",
    "University counsellors available every Thursday afternoon.",
    "Research Centre announces breakthrough in quantum education.",
    "Your hard work is building the future of knowledge!",
    "Lost & Found: one red pencil case — inquire at reception.",
    "Exam timetables are posted on the notice board.",
    "Staff vs Students football match this Friday at 4pm!",
    "Knowledge is power — keep studying, Edu Empire!",
    "Budget approved for new classroom wing — groundbreaking next term.",
    "Student council elections open. Cast your vote today!",
    "Recycling initiative launched across all campus buildings.",
    "Innovation Hub hosts its first interdisciplinary symposium!",
    "Space Academy students complete their first zero-G simulation.",
    "World Campus live-streams lectures to 50 countries.",
    "Quantum Institute achieves first quantum entanglement experiment.",
    "The Nexus of Knowledge has been named a World Heritage Site.",
]
