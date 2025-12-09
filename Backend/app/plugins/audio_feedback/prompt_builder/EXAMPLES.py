# Example Usage - Report Generator Varianten
# 
# Dieses Script zeigt, wie man die verschiedenen Report-Varianten verwendet
# und Configs für Forschungs-Experimente erstellt.

from prompt_builder.prompt_generator import PromptGenerator
from prompt_builder.report_config import ReportConfig, FEATURE_SETS

# =============================================================================
# BEISPIEL 1: Standard Detailed Report (Default)
# =============================================================================

def example_detailed_report():
    """Standard: Detaillierter pädagogischer Report."""
    
    # Einfachste Verwendung (Standard = Detailed)
    prompt_gen = PromptGenerator()
    
    # Oder explizit
    prompt_gen = PromptGenerator(report_variant='detailed')
    
    # Oder mit Config
    config = ReportConfig.detailed_report()
    prompt_gen = PromptGenerator('detailed', config)
    
    print("✅ Detailed Report Generator erstellt")
    return prompt_gen


# =============================================================================
# BEISPIEL 2: Technical Report (Feature-Extraktion)
# =============================================================================

def example_technical_report():
    """Technischer Report ohne pädagogische Interpretation."""
    
    config = ReportConfig.technical_report()
    prompt_gen = PromptGenerator('technical', config)
    
    print("✅ Technical Report Generator erstellt")
    print("   - Rohe Feature-Daten")
    print("   - Keine Interpretationen")
    print("   - Gruppierung nach Analyse-Typ")
    
    return prompt_gen


# =============================================================================
# BEISPIEL 3: Selective Report mit Feature-Subset
# =============================================================================

def example_selective_report_minimal():
    """Minimaler Report mit nur 3 Features."""
    
    # Nur die wichtigsten Features
    config = ReportConfig(
        enabled_features=['tempo', 'mean_pitch', 'mean_rms'],
        format_style='box',
        include_interpretations=True
    )
    
    prompt_gen = PromptGenerator('selective', config)
    
    print("✅ Selective Report Generator erstellt (Minimal)")
    print("   - Nur 3 Features: tempo, mean_pitch, mean_rms")
    
    return prompt_gen


def example_selective_report_rhythm_focus():
    """Report fokussiert auf Rhythmus."""
    
    # Nutze vordefiniertes Feature-Set
    config = ReportConfig(
        enabled_features=FEATURE_SETS['rhythm_focus'],
        format_style='box',
        include_interpretations=True
    )
    
    prompt_gen = PromptGenerator('selective', config)
    
    print("✅ Selective Report Generator erstellt (Rhythm Focus)")
    print(f"   - Features: {FEATURE_SETS['rhythm_focus']}")
    
    return prompt_gen


def example_selective_report_without_comparisons():
    """Report ohne Vergleichsmetriken."""
    
    config = ReportConfig(
        format_style='box',
        include_comparisons=False,  # Keine Vergleiche
        include_interpretations=True
    )
    
    prompt_gen = PromptGenerator('selective', config)
    
    print("✅ Selective Report Generator erstellt (No Comparisons)")
    print("   - Alle Features außer Vergleichsmetriken")
    
    return prompt_gen


# =============================================================================
# BEISPIEL 4: Experimentelle Configs
# =============================================================================

def example_experiment_ablation_study():
    """A/B-Testing: Welche Features sind wichtig?"""
    
    experiments = {
        'baseline': ReportConfig.detailed_report(),
        
        'no_vibrato': ReportConfig(
            enabled_features=[
                'tempo', 'onset_count', 'rhythm_std_interval',
                'mean_pitch', 'estimated_key', 'dominant_chord',
                # vibrato_strength weggelassen
                'mean_rms', 'dynamic_range_db'
            ]
        ),
        
        'tempo_only': ReportConfig(
            enabled_features=FEATURE_SETS['tempo_only']
        ),
        
        'pitch_only': ReportConfig(
            enabled_features=FEATURE_SETS['pitch_only']
        )
    }
    
    generators = {}
    for name, config in experiments.items():
        generators[name] = PromptGenerator('selective', config)
        print(f"✅ Experiment '{name}' konfiguriert")
    
    return generators


def example_experiment_token_optimization():
    """Finde minimales Feature-Set für gute Ergebnisse."""
    
    feature_combinations = [
        ['tempo'],
        ['tempo', 'mean_pitch'],
        ['tempo', 'mean_pitch', 'mean_rms'],
        ['tempo', 'mean_pitch', 'mean_rms', 'dtw_distance'],
        FEATURE_SETS['minimal_core'],
    ]
    
    generators = []
    for i, features in enumerate(feature_combinations):
        config = ReportConfig(
            enabled_features=features,
            format_style='plain',  # Spart Tokens
            include_interpretations=False  # Spart Tokens
        )
        gen = PromptGenerator('selective', config)
        generators.append((f"combo_{i+1}", gen, len(features)))
        print(f"✅ Kombination {i+1}: {len(features)} Features")
    
    return generators


def example_experiment_format_comparison():
    """Vergleiche verschiedene Formatierungsstile."""
    
    formats = {
        'box': ReportConfig(format_style='box'),
        'plain': ReportConfig(format_style='plain'),
    }
    
    generators = {}
    for name, config in formats.items():
        generators[name] = PromptGenerator('selective', config)
        print(f"✅ Format '{name}' konfiguriert")
    
    return generators


# =============================================================================
# BEISPIEL 5: Custom Config
# =============================================================================

def example_custom_research_config():
    """Vollständig angepasste Config für spezifisches Experiment."""
    
    config = ReportConfig(
        # Nur ausgewählte Features
        enabled_features=[
            'tempo',
            'mean_pitch', 
            'mean_rms',
            'dtw_distance',
            'pitch_contour_correlation'
        ],
        
        # Formatierung
        format_style='box',
        
        # Kontext & Interpretationen
        include_context=True,
        include_interpretations=True,
        include_comparisons=True,
        
        # Detail-Level
        verbosity_level='normal',
        
        # Werte-Anzeige
        show_reference_values=True,
        show_student_values=True,
        
        # Kategorien-Reihenfolge
        category_order=['tempo_rhythm', 'pitch_harmony', 'comparison']
    )
    
    prompt_gen = PromptGenerator('selective', config)
    
    print("✅ Custom Research Config erstellt")
    print("   - 5 ausgewählte Features")
    print("   - Box-Format mit Interpretationen")
    print("   - Custom Kategorien-Reihenfolge")
    
    return prompt_gen


# =============================================================================
# VERWENDUNG IN DER PIPELINE
# =============================================================================

def usage_in_pipeline(segment_results):
    """Zeigt Verwendung in der AudioFeedbackPipeline."""
    
    # 1. Generator erstellen (einmalig, z.B. im __init__)
    config = ReportConfig.detailed_report()
    prompt_gen = PromptGenerator('detailed', config)
    
    # 2. Feedback generieren (für jede Analyse)
    result = prompt_gen.generate_feedback_prompt(
        segment_results=segment_results,
        language='Deutsch',
        referenz_instrument='Klavier',
        schueler_instrument='Gitarre',
        personal_message='Fokussiere auf Rhythmus-Genauigkeit.',
        use_simple_language=False
    )
    
    # 3. Ergebnis verwenden
    system_prompt = result['system_prompt']     # An LLM senden
    analysis_data = result['analysis_data']     # An LLM senden
    report_variant = result['report_variant']   # Für Logging
    
    print(f"\n{'='*70}")
    print("SYSTEM PROMPT:")
    print(f"{'='*70}")
    print(system_prompt[:200] + "...")
    
    print(f"\n{'='*70}")
    print(f"ANALYSIS DATA ({report_variant}):")
    print(f"{'='*70}")
    print(analysis_data[:500] + "...")
    
    return result


# =============================================================================
# MAIN: Alle Beispiele ausführen
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("REPORT GENERATOR EXAMPLES")
    print("="*70 + "\n")
    
    # Mock segment_results für Demos
    mock_segments = [{
        'schueler_start': 0.0,
        'schueler_end': 5.3,
        'analysis': {
            'referenz_tempo': 120.5,
            'schueler_tempo': 118.3,
            'referenz_mean_pitch': 261.63,
            'schueler_mean_pitch': 259.2,
            'dtw_distance': 4.23
        }
    }]
    
    print("\n--- BEISPIEL 1: Detailed Report ---")
    gen1 = example_detailed_report()
    
    print("\n--- BEISPIEL 2: Technical Report ---")
    gen2 = example_technical_report()
    
    print("\n--- BEISPIEL 3a: Selective Report (Minimal) ---")
    gen3a = example_selective_report_minimal()
    
    print("\n--- BEISPIEL 3b: Selective Report (Rhythm Focus) ---")
    gen3b = example_selective_report_rhythm_focus()
    
    print("\n--- BEISPIEL 3c: Selective Report (No Comparisons) ---")
    gen3c = example_selective_report_without_comparisons()
    
    print("\n--- BEISPIEL 4a: Ablation Study ---")
    gens4a = example_experiment_ablation_study()
    
    print("\n--- BEISPIEL 4b: Token Optimization ---")
    gens4b = example_experiment_token_optimization()
    
    print("\n--- BEISPIEL 4c: Format Comparison ---")
    gens4c = example_experiment_format_comparison()
    
    print("\n--- BEISPIEL 5: Custom Research Config ---")
    gen5 = example_custom_research_config()
    
    print("\n--- USAGE: In Pipeline ---")
    result = usage_in_pipeline(mock_segments)
    
    print("\n" + "="*70)
    print("✅ Alle Beispiele erfolgreich ausgeführt!")
    print("="*70 + "\n")
    
    print("📝 Siehe REPORT_DOCUMENTATION.md für vollständige Dokumentation")
