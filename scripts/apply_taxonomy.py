"""
apply_taxonomy.py — Applique la nouvelle taxonomie aux frontmatters SKILL.md
"""
import os
import re
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================
# RÈGLES DE TAXONOMIE
# Format : (pattern_fn, category)
# La première règle qui matche gagne.
# ============================================================

def matches(skill_id, *keywords):
    return any(k in skill_id for k in keywords)

def starts(skill_id, *prefixes):
    return any(skill_id.startswith(p) for p in prefixes)

TAXONOMY_RULES = [
    # ── Andruia (meta-skills propriétaires) ──────────────────
    (lambda s: starts(s, '00-andruia', '10-andruia', '20-andruia'), 'andruia'),

    # ── Cloud — Azure ─────────────────────────────────────────
    (lambda s: starts(s, 'azure-', 'azd-', 'm365-', 'microsoft-azure'), 'cloud/azure'),

    # ── Cloud — AWS ───────────────────────────────────────────
    (lambda s: starts(s, 'aws-'), 'cloud/aws'),

    # ── Cloud — GCP ───────────────────────────────────────────
    (lambda s: starts(s, 'gcp-'), 'cloud/gcp'),

    # ── Cloud — Générique ─────────────────────────────────────
    (lambda s: matches(s, 'cloud-architect', 'hybrid-cloud', 'multi-cloud', 'cloud-devops'), 'cloud/general'),

    # ── Frameworks UI — Apple HIG ─────────────────────────────
    (lambda s: starts(s, 'hig-'), 'frameworks/hig'),

    # ── Frameworks UI — Three.js ──────────────────────────────
    (lambda s: starts(s, 'threejs-'), 'frameworks/threejs'),

    # ── Frameworks UI — React ─────────────────────────────────
    (lambda s: starts(s, 'react-') and not matches(s, 'react-native'), 'frameworks/react'),

    # ── Frameworks — React Native ─────────────────────────────
    (lambda s: starts(s, 'react-native'), 'frameworks/react-native'),

    # ── Frameworks — Angular ──────────────────────────────────
    (lambda s: starts(s, 'angular'), 'frameworks/angular'),

    # ── Frameworks — Next.js ──────────────────────────────────
    (lambda s: starts(s, 'nextjs'), 'frameworks/nextjs'),

    # ── Frameworks — Expo ─────────────────────────────────────
    (lambda s: starts(s, 'expo-'), 'frameworks/expo'),

    # ── Frameworks — n8n ──────────────────────────────────────
    (lambda s: starts(s, 'n8n-'), 'frameworks/n8n'),

    # ── Frameworks — Conductor ────────────────────────────────
    (lambda s: starts(s, 'conductor-'), 'frameworks/conductor'),

    # ── Frameworks — TDD workflows ────────────────────────────
    (lambda s: starts(s, 'tdd-'), 'frameworks/tdd'),

    # ── Frameworks — fp-ts ────────────────────────────────────
    (lambda s: starts(s, 'fp-'), 'frameworks/fp-ts'),

    # ── Frameworks — Makepad ──────────────────────────────────
    (lambda s: starts(s, 'makepad-'), 'frameworks/makepad'),

    # ── Frameworks — Robius ───────────────────────────────────
    (lambda s: starts(s, 'robius-'), 'frameworks/robius'),

    # ── Frameworks — Avalonia ─────────────────────────────────
    (lambda s: starts(s, 'avalonia-'), 'frameworks/avalonia'),

    # ── Frameworks — C4 Architecture ─────────────────────────
    (lambda s: starts(s, 'c4-'), 'frameworks/c4'),

    # ── Domains — Odoo ────────────────────────────────────────
    (lambda s: starts(s, 'odoo-'), 'domains/odoo'),

    # ── Domains — SEO ─────────────────────────────────────────
    (lambda s: starts(s, 'seo-') or s == 'seo', 'domains/seo'),

    # ── Domains — Apify / Scraping ────────────────────────────
    (lambda s: starts(s, 'apify-'), 'domains/apify'),

    # ── Domains — Blockchain / Web3 ───────────────────────────
    (lambda s: matches(s, 'blockchain', 'solidity', 'defi', 'nft', 'crypto', 'lightning-'), 'domains/web3'),

    # ── Domains — Health / Medical ────────────────────────────
    (lambda s: matches(s, 'health', 'medical', 'nutrition', 'fitness', 'rehabilitation',
                           'sleep-analyzer', 'skin-health', 'oral-health', 'sexual-health',
                           'mental-health', 'occupational-health', 'tcm-', 'travel-health',
                           'weightloss', 'family-health', 'ai-analyzer'), 'domains/health'),

    # ── Domains — Finance / FinTech ───────────────────────────
    (lambda s: matches(s, 'fintech', 'plaid', 'stripe', 'payment', 'paypal', 'billing',
                           'finance', 'quant', 'monte-carlo', 'backtesting', 'risk-metric',
                           'startup-financial', 'alpha-vantage', 'market-sizing'), 'domains/finance'),

    # ── Domains — Shopify / E-commerce ───────────────────────
    (lambda s: matches(s, 'shopify', 'ecommerce', 'woocommerce'), 'domains/ecommerce'),

    # ── Domains — Wiki ────────────────────────────────────────
    (lambda s: starts(s, 'wiki-'), 'domains/wiki'),

    # ── Automation — CRM & SaaS tools ────────────────────────
    (lambda s: matches(s, 'hubspot', 'salesforce', 'pipedrive', 'close-auto',
                           'intercom', 'zendesk', 'freshdesk', 'freshservice',
                           'helpdesk'), 'automation/crm'),

    # ── Automation — Project Management ───────────────────────
    (lambda s: matches(s, 'jira', 'linear', 'asana', 'monday', 'clickup',
                           'notion', 'basecamp', 'wrike', 'todoist'), 'automation/project-management'),

    # ── Automation — Communication ────────────────────────────
    (lambda s: matches(s, 'slack', 'discord', 'telegram', 'microsoft-teams',
                           'whatsapp', 'agentmail', 'email-system', 'sendgrid',
                           'postmark', 'brevo', 'mailchimp', 'convertkit',
                           'klaviyo', 'outlook', 'gmail'), 'automation/communication'),

    # ── Automation — Productivity & Cloud storage ──────────────
    (lambda s: matches(s, 'google-docs', 'google-drive', 'google-sheets', 'google-slides',
                           'google-calendar', 'one-drive', 'dropbox', 'box-auto',
                           'canva', 'figma', 'miro', 'airtable', 'docusign',
                           'office-productivity'), 'automation/productivity'),

    # ── Automation — Monitoring & Analytics ───────────────────
    (lambda s: matches(s, 'datadog', 'pagerduty', 'sentry-auto', 'posthog',
                           'amplitude', 'mixpanel', 'segment-auto', 'google-analytics',
                           'analytics-tracking'), 'automation/analytics'),

    # ── Automation — Infra & DevOps tools ─────────────────────
    (lambda s: matches(s, 'vercel-auto', 'render-auto', 'circleci', 'bamboohr',
                           'make-auto', 'zapier', 'square-auto', 'stripe-auto'), 'automation/tools'),

    # ── Automation — Social Media ─────────────────────────────
    (lambda s: matches(s, 'instagram', 'tiktok', 'linkedin-auto', 'twitter',
                           'reddit-auto', 'youtube'), 'automation/social'),

    # ── AI / ML ───────────────────────────────────────────────
    (lambda s: starts(s, 'llm-', 'rag-', 'langchain', 'langgraph', 'crewai',
                          'pydantic-ai', 'langfuse') or
               matches(s, 'ai-agent', 'multi-agent', 'agent-eval', 'agent-memory',
                           'agent-orches', 'agent-tool', 'parallel-agent', 'subagent',
                           'agent-manager', 'agent-framework', 'hosted-agent',
                           'ai-engineer', 'ai-ml', 'mlops', 'ml-engineer',
                           'embedding', 'vector-search', 'similarity-search',
                           'prompt-caching', 'prompt-engineer', 'prompt-lib',
                           'context-manager', 'context-compression', 'context-window',
                           'context-fundamentals', 'context-degradation',
                           'context-driven', 'context-optim',
                           'llm-evaluation', 'llm-prompt', 'llm-app',
                           'hugging-face', 'gemini-api', 'imagen',
                           'computer-vision', 'ml-pipeline', 'machine-learning-ops',
                           'advanced-evaluation', 'agent-evaluation',
                           'deep-research', 'ai-agents-architect',
                           'agents-md', 'agents-v2', 'infinite-gratitude',
                           'agentfolio', 'ai-product', 'ai-wrapper',
                           'dispatching-parallel', 'bdi-mental',
                           'hierarchical-agent', 'conversation-memory',
                           'memory-system', 'fal-',
                           'autonomous-agent', 'ai-analyzer'), 'ai-ml'),

    # ── Security ──────────────────────────────────────────────
    (lambda s: matches(s, 'security', 'pentest', 'red-team', 'malware',
                           'vulnerability', 'exploit', 'burp', 'metasploit',
                           'ethical-hack', 'osint', 'penetration', 'active-directory',
                           'anti-revers', 'binary-anal', 'memory-forensic',
                           'firmware-anal', 'sast', 'semgrep', 'sql-injection',
                           'html-injection', 'idor-test', 'file-path-traversal',
                           'broken-auth', 'shodan', 'scanning-tool',
                           'attack-tree', 'stride-anal', 'threat-model',
                           'threat-mitig', 'static-anal', 'proof-of-vuln',
                           'protocol-reverse', 'privilege-escal',
                           'linux-privilege', 'constant-time',
                           'dwarf-expert', 'ffuf', 'smtp-pentest', 'ssh-pentest',
                           'sqlmap', 'web-security', 'audit-context',
                           'security-bluebook', 'security-skill',
                           'golang-security', 'python-security', 'rust-security',
                           'building-secure', 'pci-compliance', 'gdpr',
                           'differential-review', 'secrets-manage',
                           'varlock', 'monte-carlo-vuln',
                           'supply-chain-risk', 'agentic-actions-audit'), 'security'),

    # ── Languages — Python ────────────────────────────────────
    (lambda s: starts(s, 'python-') or s in ('python-pro',), 'languages/python'),

    # ── Languages — TypeScript / JavaScript ───────────────────
    (lambda s: matches(s, 'typescript', 'javascript-pro', 'javascript-mastery',
                           'javascript-testing', 'modern-javascript', 'bun-development',
                           'javascript-typescript'), 'languages/typescript'),

    # ── Languages — Go ────────────────────────────────────────
    (lambda s: starts(s, 'golang', 'go-') or s == 'go-concurrency-patterns', 'languages/go'),

    # ── Languages — Rust ──────────────────────────────────────
    (lambda s: starts(s, 'rust-') or s in ('rust-pro',), 'languages/rust'),

    # ── Languages — Java ──────────────────────────────────────
    (lambda s: s in ('java-pro',) or starts(s, 'kotlin-'), 'languages/java'),

    # ── Languages — C / C++ ───────────────────────────────────
    (lambda s: s in ('c-pro', 'cpp-pro', 'arm-cortex-expert'), 'languages/c'),

    # ── Languages — C# / .NET ─────────────────────────────────
    (lambda s: matches(s, 'csharp', 'dotnet-', 'azure-functions'), 'languages/dotnet'),

    # ── Languages — Ruby / Rails ──────────────────────────────
    (lambda s: matches(s, 'ruby-pro', 'rails', 'new-rails'), 'languages/ruby'),

    # ── Languages — PHP / Laravel ─────────────────────────────
    (lambda s: matches(s, 'php-pro', 'laravel'), 'languages/php'),

    # ── Languages — Elixir ────────────────────────────────────
    (lambda s: s == 'elixir-pro', 'languages/elixir'),

    # ── Languages — Scala / Haskell / Julia ───────────────────
    (lambda s: s in ('scala-pro', 'haskell-pro', 'julia-pro'), 'languages/functional'),

    # ── Languages — SQL ───────────────────────────────────────
    (lambda s: s in ('sql-pro', 'sql-optimization-patterns') or starts(s, 'sql-'), 'languages/sql'),

    # ── Languages — Bash / Shell ──────────────────────────────
    (lambda s: matches(s, 'bash-', 'bash-pro', 'linux-shell', 'posix-shell',
                           'busybox', 'os-scripting', 'powershell'), 'languages/shell'),

    # ── Database ──────────────────────────────────────────────
    (lambda s: matches(s, 'database', 'postgres', 'postgresql', 'neon-postgres',
                           'mongodb', 'nosql', 'drizzle', 'prisma', 'dbt-',
                           'database-admin', 'database-arch', 'database-design',
                           'database-migrat', 'database-optim', 'database-cloud',
                           'claimable-postgres', 'azure-cosmos', 'azure-data-tables',
                           'dbos-'), 'database'),

    # ── DevOps & Infrastructure ───────────────────────────────
    (lambda s: matches(s, 'docker', 'kubernetes', 'k8s-', 'helm-', 'terraform',
                           'ansible', 'gitops', 'cicd', 'deployment', 'devcontainer',
                           'devops', 'gitlab-ci', 'github-actions', 'jenkins',
                           'prometheus', 'grafana', 'istio', 'linkerd',
                           'service-mesh', 'distributed-trac', 'observability',
                           'slo-implem', 'incident-', 'on-call', 'postmortem',
                           'server-manage', 'linux-trouble', 'network-',
                           'mtls-', 'loki-mode', 'airflow'), 'devops'),

    # ── Frontend & Design ─────────────────────────────────────
    (lambda s: matches(s, 'frontend-design', 'frontend-dev', 'frontend-developer',
                           'frontend-ui', 'frontend-slide', 'frontend-mobile-dev',
                           'ui-skills', 'ui-ux', 'web-design', 'web-artifacts',
                           'canvas-design', 'design-md', 'design-spell',
                           'tailwind', 'shadcn', 'radix-ui',
                           'scroll-experience', 'baseline-ui',
                           'stitch-', 'remotion', 'theme-factory',
                           'font-', 'favicon', 'generate-image', 'algo-art',
                           'web-games', 'animation', 'magic-animat',
                           'shader-programm', 'animejs',
                           'nanobanana-ppt', 'frontend-slides',
                           'interactive-port'), 'frontend/design'),

    # ── Frontend — CRO / Marketing ────────────────────────────
    (lambda s: matches(s, '-cro', 'form-cro', 'page-cro', 'onboarding-cro',
                           'signup-flow-cro', 'popup-cro', 'paywall-upgrade',
                           'referral-program', 'free-tool-strat', 'launch-strat'), 'frontend/cro'),

    # ── Mobile ────────────────────────────────────────────────
    (lambda s: matches(s, 'ios-developer', 'swiftui', 'flutter', 'mobile-design',
                           'mobile-developer', 'mobile-security', 'building-native-ui',
                           'android-jetpack', 'android_ui', 'app-store-optim'), 'mobile'),

    # ── Testing & QA ──────────────────────────────────────────
    (lambda s: matches(s, 'testing-qa', 'testing-pattern', 'test-driven',
                           'e2e-testing', 'playwright', 'webapp-testing', 'test-autom',
                           'test-fixing', 'test-driven', 'bats-testing',
                           'javascript-testing', 'python-testing',
                           'performance-testing', 'web3-testing',
                           'e2e-testing-patt', 'testing-hand',
                           'tdd-orchestrator') and not matches(s, 'tdd-workflow', 'tdd-workflows'),
                           'testing'),

    # ── Game Development ──────────────────────────────────────
    (lambda s: starts(s, 'game-development') or
               matches(s, 'godot', 'unity-', 'bevy-', 'minecraft',
                           '2d-games', '3d-games', 'web-games'), 'games'),

    # ── Documentation & Writing ───────────────────────────────
    (lambda s: matches(s, 'documentation', 'api-documentation', 'api-documenter',
                           'readme', 'doc-coauthor', 'documentation-gen',
                           'documentation-templ', 'beautiful-prose',
                           'scientific-writing', 'copy-edit', 'blog-writing',
                           'content-creator', 'copywriting', 'avoid-ai-writing',
                           'writing-plan', 'writing-skill', 'social-content',
                           'paper-analysis', 'literature', 'citation-manage',
                           'podcast-gen', 'internal-comms', 'professional-proof',
                           'skill-writer'), 'content/writing'),

    # ── Architecture & Design Patterns ────────────────────────
    (lambda s: matches(s, 'architect-review', 'architecture-decision',
                           'architecture-patt', 'backend-architect',
                           'software-architect', 'cloud-architect',
                           'senior-architect', 'ddd-', 'domain-driven',
                           'cqrs-', 'event-sourc', 'event-store',
                           'saga-orchestr', 'projection-patt',
                           'microservices', 'monorepo-arch',
                           'graphql-arch', 'api-design-princ',
                           'api-patt', 'backend-dev-guide',
                           'backend-development', 'database-arch'), 'architecture'),

    # ── Development Tools / Workflow ──────────────────────────
    (lambda s: matches(s, 'git-', 'github-', 'create-pr', 'pr-writer',
                           'address-github', 'iterate-pr', 'commit',
                           'create-branch', 'git-pushing', 'changelog',
                           'gh-review', 'gitlab-auto', 'github-issue',
                           'github-workflow'), 'tooling/git'),

    # ── Skill Management (meta) ────────────────────────────────
    (lambda s: matches(s, 'skill-creator', 'skill-developer', 'skill-improver',
                           'skill-writer', 'skill-scanner', 'skill-seekers',
                           'skill-router', 'using-superpowers', 'superpowers-lab',
                           'skill-creator-ms', 'antigravity-workflow',
                           'manifest', 'blockrun', 'plan-writing',
                           'planning-with-files', 'executing-plans',
                           'concise-planning', 'writing-plans',
                           'behavioral-modes', 'moyu', 'ask-questions',
                           'clarity-gate', 'context7-auto'), 'meta'),

    # ── Business & Product ────────────────────────────────────
    (lambda s: matches(s, 'product-manager', 'business-analyst', 'startup-',
                           'market-sizing', 'pricing-strat', 'competitive-',
                           'competitor-alt', 'launch-strat', 'saas-mvp',
                           'micro-saas', 'app-builder', 'personal-tool',
                           'hr-pro', 'legal-advisor', 'culture-index',
                           'customer-support', 'sales-automator',
                           'marketing-ideas', 'marketing-psych',
                           'kpi-dashboard', 'paid-ads'), 'business'),

    # ── Spécifiques communauté sans catégorie claire ───────────
    (lambda s: True, 'uncategorized'),  # fallback
]

def get_category(skill_id):
    for rule_fn, category in TAXONOMY_RULES:
        try:
            if rule_fn(skill_id):
                return category
        except Exception:
            pass
    return 'uncategorized'


def update_skill_frontmatter(skill_path, new_category):
    """Met à jour le champ category dans le frontmatter YAML d'un SKILL.md"""
    with open(skill_path, 'r', encoding='utf-8') as f:
        content = f.read()

    fm_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        # Pas de frontmatter — on en ajoute un minimal
        new_content = f'---\ncategory: {new_category}\n---\n\n' + content
        with open(skill_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)
        return 'added'

    fm_text = fm_match.group(1)

    if 'category:' in fm_text:
        # Remplacer la valeur existante
        new_fm = re.sub(r'^category:.*$', f'category: {new_category}', fm_text, flags=re.MULTILINE)
    else:
        # Ajouter après la première ligne
        lines = fm_text.split('\n')
        lines.insert(1, f'category: {new_category}')
        new_fm = '\n'.join(lines)

    new_content = content[:fm_match.start(1)] + new_fm + content[fm_match.end(1):]
    with open(skill_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)
    return 'updated'


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skills_dir = os.path.join(base_dir, 'skills')

    stats = {}
    updated = 0
    errors = []

    for root, dirs, files in os.walk(skills_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        if 'SKILL.md' not in files:
            continue

        skill_id = os.path.basename(root)
        skill_md = os.path.join(root, 'SKILL.md')
        category = get_category(skill_id)

        stats[category] = stats.get(category, 0) + 1

        try:
            update_skill_frontmatter(skill_md, category)
            updated += 1
        except Exception as e:
            errors.append(f'{skill_id}: {e}')

    print(f'\n✅ Mis à jour: {updated} skills')
    print(f'❌ Erreurs: {len(errors)}')
    for e in errors[:10]:
        print(f'  {e}')

    print('\n=== Distribution par catégorie ===')
    for cat, count in sorted(stats.items(), key=lambda x: (-x[1], x[0])):
        print(f'  {cat}: {count}')

if __name__ == '__main__':
    main()
