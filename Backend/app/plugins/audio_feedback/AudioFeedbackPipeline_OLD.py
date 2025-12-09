# AudioFeedbackPipeline - Hauptklasse für die Audio-Analyse und Feedback-Generierung
# Analysiert Audio-Features und erstellt strukturierte Feedback-Prompts für Musikschüler
#
# Diese Klasse ist Teil des Audio Feedback Plugins und enthält die Kern-Logik
# für die Feature-Extraktion, Vergleichsanalyse und Feedback-Generierung.

import os
import librosa  # Haupt-Bibliothek für Audio-Analyse
import soundfile as sf  # Audio-Datei Ein-/Ausgabe
import numpy as np  # Numerische Berechnungen und Array-Operationen
import scipy.spatial  # Distanzberechnungen zwischen Audio-Features
import itertools  # Hilfsfunktionen für Iterationen
from collections import Counter


class AudioFeedbackPipeline:
    """Hauptklasse für die Analyse von Audio-Aufnahmen und Feedback-Generierung.

    Diese Klasse führt eine umfassende Audio-Analyse durch, vergleicht Schüler-
    und Referenzaufnahmen und generiert strukturierte Feedback-Prompts.

    Analysierte Features umfassen:
    - Tempo und Rhythmus
    - Tonhöhe und Harmonie
    - Lautstärke und Dynamik
    - Klangfarbe und spektrale Eigenschaften
    - Artikulation und Phrasierung
    """

    def __init__(
        self, upload_folder: str, target_sr: int = 22050, target_length: int = 30
    ):
        """Initialisiert die Audio-Feedback-Pipeline.

        Args:
            upload_folder: Pfad zum Ordner mit den Audio-Dateien
            target_sr: Ziel-Sample-Rate für Audio-Verarbeitung (Standard: 22050 Hz)
            target_length: Maximale Länge für Audio-Verarbeitung in Sekunden (Standard: 30s)
        """
        self.upload_folder = upload_folder
        self.preprocessed_data = {}  # Cache für vorverarbeitete Audio-Daten
        self.target_sr = target_sr
        self.target_length = target_length

        # Liste aller verfügbaren Analyse-Funktionen
        # Jede Funktion analysiert einen spezifischen Audio-Aspekt
        self.analysis_functions = [
            ("tempo", self.analyze_tempo),  # Geschwindigkeit/BPM
            ("length", self.analyze_length),  # Aufnahmedauer
            ("loudness", self.analyze_loudness),  # Gesamtlautstärke
            ("pitch", self.analyze_pitch),  # Grundfrequenz/Tonhöhe
            ("dynamics", self.analyze_dynamics),  # Lautstärke-Variationen
            ("spectral_centroid", self.analyze_spectral_centroid),  # Klangfarbe
            ("onset_count", self.analyze_onset_count),  # Anzahl Noteneinsätze
            (
                "rhythm_stability",
                self.analyze_rhythm_stability,
            ),  # Rhythmus-Gleichmäßigkeit
            ("spectral_bandwidth", self.analyze_spectral_bandwidth),  # Frequenzbreite
            ("spectral_rolloff", self.analyze_spectral_rolloff),  # Hochfrequenz-Anteil
            ("silences", self.analyze_silences),  # Pausen-Analyse
            ("zero_crossing_rate", self.analyze_zero_crossing_rate),  # Rauschanteil
            (
                "mel-frequency cepstral coefficients",
                self.analyze_mfcc,
            ),  # Klangfarbe-Features
            ("chroma-key", self.analyze_chroma_key),  # Tonart-Erkennung
            ("chord_histogram", self.analyze_chord_histogram),  # Akkord-Verteilung
            ("attack_time", self.analyze_attack_time),  # Anschlag-Geschwindigkeit
            ("vibrato", self.analyze_vibrato),  # Vibrato-Analyse
            (
                "timbre_consistency",
                self.analyze_timbre_consistency,
            ),  # Klangfarbe-Konstanz
            ("polyphony", self.analyze_polyphony),  # Mehrstimmigkeit
        ]

    def preprocess_audio(self, filename):
        """Lädt eine Audiodatei und gibt (y, sr) zurück."""
        # Zuerst im Upload-Ordner suchen
        path = os.path.join(self.upload_folder, filename)

        # Falls nicht gefunden, im segments Unterordner suchen
        if not os.path.exists(path):
            segments_path = os.path.join(self.upload_folder, "segments", filename)
            if os.path.exists(segments_path):
                path = segments_path
            else:
                raise FileNotFoundError(
                    f"Die Datei existiert nicht: {filename} (gesucht in {self.upload_folder} und {os.path.join(self.upload_folder, 'segments')})"
                )

        y, sr = librosa.load(path)
        return y, sr

    def analyze_all(self, referenz_fn, schueler_fn):
        """Führt eine vollständige Audio-Analyse für beide Dateien durch.

        Analysiert sowohl individuelle Features jeder Datei als auch
        Vergleichsmetriken zwischen Referenz und Schüler-Aufnahme.

        Args:
            referenz_fn: Dateiname der Referenz-Aufnahme
            schueler_fn: Dateiname der Schüler-Aufnahme

        Returns:
            dict: Vollständige Analyse-Ergebnisse mit individuellen und Vergleichs-Features
        """
        results = {}

        # Lade und vorverarbeite beide Audio-Dateien
        ref_data = self.preprocess_audio(referenz_fn)
        sch_data = self.preprocess_audio(schueler_fn)

        # Führe alle individuellen Analysen für beide Dateien durch
        for name, func in self.analysis_functions:
            results[f"referenz_{name}"] = func(ref_data)
            results[f"schueler_{name}"] = func(sch_data)

        # Führe Vergleichsanalysen zwischen beiden Aufnahmen durch
        # Diese Metriken messen die Ähnlichkeit/Unterschiede zwischen den Aufnahmen

        # MFCC-Distanz: Misst Unterschiede in der Klangfarbe
        mfcc_dist = self.analyze_mfcc_distance(ref_data, sch_data)
        results["mfcc_distance"] = mfcc_dist["mfcc_distance"]

        # Chroma-Ähnlichkeit: Vergleicht harmonische Inhalte
        chroma_sim = self.analyze_chroma_similarity(ref_data, sch_data)
        results["chroma_similarity"] = chroma_sim["chroma_similarity"]

        # RMS-Korrelation: Vergleicht Lautstärke-Verläufe
        rms_corr = self.analyze_rms_correlation(ref_data, sch_data)
        results["rms_correlation"] = rms_corr["rms_correlation"]

        # DTW-Distanz: Misst zeitliche Ausrichtung und Ähnlichkeit
        dtw_dist = self.analyze_dtw_distance(ref_data, sch_data)
        results["dtw_distance"] = dtw_dist["dtw_distance"]

        # Energie-Hüllkurven-Ähnlichkeit: Vergleicht Dynamik-Verläufe
        envelope_sim = self.analyze_energy_envelope_similarity(ref_data, sch_data)
        results["energy_envelope_correlation"] = envelope_sim[
            "energy_envelope_correlation"
        ]

        # Tonhöhen-Kontur-Ähnlichkeit: Vergleicht Melodie-Verläufe
        pitch_contour_sim = self.analyze_pitch_contour_similarity(ref_data, sch_data)
        results["pitch_contour_correlation"] = pitch_contour_sim[
            "pitch_contour_correlation"
        ]

        return results

    def analyze_tempo(self, data):
        y, sr = data
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        return float(tempo)

    def analyze_length(self, data):
        y, sr = data
        duration = len(y) / sr  # Dauer in Sekunden
        return duration

    def analyze_loudness(self, data):
        y, sr = data
        n_fft = min(2048, len(y))
        rms = librosa.feature.rms(y=y, frame_length=n_fft)[0]
        mean_rms = np.mean(rms)
        max_rms = np.max(rms)
        min_rms = np.min(rms)
        return {"mean_rms": mean_rms, "max_rms": max_rms, "min_rms": min_rms}

    def analyze_pitch(self, data):
        y, sr = data
        pitches = librosa.yin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
        )
        valid_pitches = pitches[pitches > 0]
        if len(valid_pitches) > 0:
            mean_pitch = float(np.mean(valid_pitches))
            min_pitch = float(np.min(valid_pitches))
            max_pitch = float(np.max(valid_pitches))
        else:
            mean_pitch = min_pitch = max_pitch = 0.0
        return {
            "mean_pitch": mean_pitch,
            "min_pitch": min_pitch,
            "max_pitch": max_pitch,
        }

    def analyze_dynamics(self, data):
        y, sr = data
        n_fft = min(2048, len(y))
        rms = librosa.feature.rms(y=y, frame_length=n_fft)[0]
        rms_db = librosa.amplitude_to_db(rms, ref=np.max)
        dynamic_range = float(np.max(rms_db) - np.min(rms_db))
        dynamic_std = float(np.std(rms_db))
        return {"dynamic_range_db": dynamic_range, "dynamic_std_db": dynamic_std}

    def analyze_spectral_centroid(self, data):
        y, sr = data
        n_fft = min(2048, len(y))
        centroids = librosa.feature.spectral_centroid(y=y, sr=sr, n_fft=n_fft)[0]
        mean_centroid = float(np.mean(centroids))
        min_centroid = float(np.min(centroids))
        max_centroid = float(np.max(centroids))
        return {
            "mean_centroid": mean_centroid,
            "min_centroid": min_centroid,
            "max_centroid": max_centroid,
        }

    def analyze_onset_count(self, data):
        y, sr = data
        onsets = librosa.onset.onset_detect(y=y, sr=sr)
        return int(len(onsets))

    def analyze_rhythm_stability(self, data):
        y, sr = data
        onsets = librosa.onset.onset_detect(y=y, sr=sr, units="time")
        if len(onsets) < 2:
            return None  # zu wenig Daten
        intervals = np.diff(onsets)  # Abstand zwischen den Onsets
        std_interval = float(np.std(intervals))
        mean_interval = float(np.mean(intervals))
        return {"std_interval": std_interval, "mean_interval": mean_interval}

    def analyze_spectral_bandwidth(self, data):
        y, sr = data
        n_fft = min(2048, len(y))
        bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, n_fft=n_fft)[0]
        mean_bw = float(np.mean(bandwidth))
        min_bw = float(np.min(bandwidth))
        max_bw = float(np.max(bandwidth))
        return {
            "mean_bandwidth": mean_bw,
            "min_bandwidth": min_bw,
            "max_bandwidth": max_bw,
        }

    def analyze_spectral_rolloff(self, data):
        y, sr = data
        n_fft = min(2048, len(y))
        rolloff = librosa.feature.spectral_rolloff(
            y=y, sr=sr, roll_percent=0.85, n_fft=n_fft
        )[0]
        mean_rolloff = float(np.mean(rolloff))
        min_rolloff = float(np.min(rolloff))
        max_rolloff = float(np.max(rolloff))
        return {
            "mean_rolloff": mean_rolloff,
            "min_rolloff": min_rolloff,
            "max_rolloff": max_rolloff,
        }

    def analyze_silences(self, data, top_db=30):
        y, sr = data
        intervals = librosa.effects.split(y, top_db=top_db)
        total_duration = len(y) / sr
        music_duration = sum((end - start) for start, end in intervals) / sr
        silence_duration = total_duration - music_duration
        num_silences = max(0, len(intervals) - 1)
        longest_silence = 0.0
        if len(intervals) > 1:
            silences = [
                (intervals[i][0], intervals[i + 1][0])
                for i in range(len(intervals) - 1)
            ]
            longest_silence = max((b - a) / sr for a, b in silences)
        return {
            "num_silences": num_silences,
            "total_silence_duration": silence_duration,
            "longest_silence": longest_silence,
        }

    def analyze_zero_crossing_rate(self, data):
        y, sr = data
        n_fft = min(2048, len(y))
        zcr = librosa.feature.zero_crossing_rate(y, frame_length=n_fft)[0]
        mean_zcr = float(np.mean(zcr))
        min_zcr = float(np.min(zcr))
        max_zcr = float(np.max(zcr))
        return {"mean_zcr": mean_zcr, "min_zcr": min_zcr, "max_zcr": max_zcr}

    def analyze_mfcc(self, data, n_mfcc=13):
        y, sr = data
        n_fft = min(2048, len(y))
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, n_fft=n_fft)
        mfcc_means = np.mean(mfccs, axis=1)
        mfcc_vars = np.var(mfccs, axis=1)
        return {
            "mfcc_mean_1": float(mfcc_means[0]),
            "mfcc_mean_2": float(mfcc_means[1]),
            "mfcc_mean_3": float(mfcc_means[2]),
            "mfcc_var_1": float(mfcc_vars[0]),
            "mfcc_var_2": float(mfcc_vars[1]),
            "mfcc_var_3": float(mfcc_vars[2]),
        }

    def analyze_chroma_key(self, data):
        y, sr = data
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_sums = np.sum(chroma, axis=1)
        # Index des Maximums entspricht Tonart-Root (C=0, C#=1, ..., B=11)
        key_idx = np.argmax(chroma_sums)
        key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        key = key_names[key_idx]
        return {"estimated_key": key}

    def analyze_mfcc_distance(self, ref_data, sch_data, n_mfcc=13):
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        n_fft = min(2048, len(y_ref), len(y_sch))
        mfcc_ref = np.mean(
            librosa.feature.mfcc(y=y_ref, sr=sr_ref, n_mfcc=n_mfcc, n_fft=n_fft), axis=1
        )
        mfcc_sch = np.mean(
            librosa.feature.mfcc(y=y_sch, sr=sr_sch, n_mfcc=n_mfcc, n_fft=n_fft), axis=1
        )
        distance = float(scipy.spatial.distance.euclidean(mfcc_ref, mfcc_sch))
        return {"mfcc_distance": distance}

    def analyze_chroma_similarity(self, ref_data, sch_data):
        from sklearn.metrics.pairwise import cosine_similarity

        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        chroma_ref = librosa.feature.chroma_cqt(y=y_ref, sr=sr_ref)
        chroma_sch = librosa.feature.chroma_cqt(y=y_sch, sr=sr_sch)
        # Mittelwert über die Zeit
        chroma_ref_mean = np.mean(chroma_ref, axis=1).reshape(1, -1)
        chroma_sch_mean = np.mean(chroma_sch, axis=1).reshape(1, -1)
        similarity = float(cosine_similarity(chroma_ref_mean, chroma_sch_mean)[0, 0])
        return {"chroma_similarity": similarity}

    def analyze_rms_correlation(self, ref_data, sch_data):
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        n_fft = min(2048, len(y_ref), len(y_sch))
        rms_ref = librosa.feature.rms(y=y_ref, frame_length=n_fft)[0]
        rms_sch = librosa.feature.rms(y=y_sch, frame_length=n_fft)[0]
        min_len = min(len(rms_ref), len(rms_sch))
        rms_ref = rms_ref[:min_len]
        rms_sch = rms_sch[:min_len]
        if min_len > 1:
            corr = float(np.corrcoef(rms_ref, rms_sch)[0, 1])
        else:
            corr = None
        return {"rms_correlation": corr}

    def analyze_dtw_distance(self, ref_data, sch_data, n_mfcc=13):
        from librosa.sequence import dtw

        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        n_fft = min(2048, len(y_ref), len(y_sch))
        mfcc_ref = librosa.feature.mfcc(y=y_ref, sr=sr_ref, n_mfcc=n_mfcc, n_fft=n_fft)
        mfcc_sch = librosa.feature.mfcc(y=y_sch, sr=sr_sch, n_mfcc=n_mfcc, n_fft=n_fft)
        min_frames = min(mfcc_ref.shape[1], mfcc_sch.shape[1])
        mfcc_ref = mfcc_ref[:, :min_frames]
        mfcc_sch = mfcc_sch[:, :min_frames]
        D, wp = dtw(X=mfcc_ref, Y=mfcc_sch, metric="euclidean")
        dtw_dist = float(D[-1, -1])
        return {"dtw_distance": dtw_dist}

    def analyze_energy_envelope_similarity(self, ref_data, sch_data):
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        n_fft = min(2048, len(y_ref), len(y_sch))
        frame_length = n_fft
        hop_length = min(512, frame_length // 2)
        energy_ref = librosa.feature.rms(
            y=y_ref, frame_length=frame_length, hop_length=hop_length
        )[0]
        energy_sch = librosa.feature.rms(
            y=y_sch, frame_length=frame_length, hop_length=hop_length
        )[0]
        min_len = min(len(energy_ref), len(energy_sch))
        if min_len < 2:
            return {"energy_envelope_correlation": None}
        energy_ref = energy_ref[:min_len]
        energy_sch = energy_sch[:min_len]
        correlation = float(np.corrcoef(energy_ref, energy_sch)[0, 1])
        return {"energy_envelope_correlation": correlation}

    def analyze_pitch_contour_similarity(self, ref_data, sch_data):
        y_ref, sr_ref = ref_data
        y_sch, sr_sch = sch_data
        # Pitch contour mit YIN berechnen
        pitch_ref = librosa.yin(
            y_ref,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr_ref,
        )
        pitch_sch = librosa.yin(
            y_sch,
            fmin=librosa.note_to_hz("C2"),
            fmax=librosa.note_to_hz("C7"),
            sr=sr_sch,
        )
        # Optional: nur gültige (nicht-Null) Werte verwenden
        valid_ref = pitch_ref[pitch_ref > 0]
        valid_sch = pitch_sch[pitch_sch > 0]
        min_len = min(len(valid_ref), len(valid_sch))
        if min_len < 2:
            return {"pitch_contour_correlation": None}
        # Kürzen auf gleiche Länge
        valid_ref = valid_ref[:min_len]
        valid_sch = valid_sch[:min_len]
        corr = float(np.corrcoef(valid_ref, valid_sch)[0, 1])
        return {"pitch_contour_correlation": corr}

    def analyze_chord_histogram(self, data):
        y, sr = data
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        major_template = np.array([1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0])
        minor_template = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0])
        templates = []
        names = []
        for i in range(12):
            templates.append(np.roll(major_template, i))
            names.append(
                ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][i]
                + "-Dur"
            )
            templates.append(np.roll(minor_template, i))
            names.append(
                ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][i]
                + "-Moll"
            )
        templates = np.array(templates)
        chords = []
        for frame in chroma.T:
            sims = [np.dot(frame, tpl) for tpl in templates]
            chord = names[np.argmax(sims)]
            chords.append(chord)
        from collections import Counter

        chord_counts = Counter(chords)
        most_common = chord_counts.most_common(3)
        return {"most_common_chords": [c for c, _ in most_common]}

    def analyze_attack_time(self, data, threshold=0.2):
        y, sr = data
        envelope = librosa.onset.onset_strength(y=y, sr=sr)
        th = threshold * np.max(envelope)
        onset_idxs = np.flatnonzero(envelope > th)
        if len(onset_idxs) > 1:
            attack_time = float(np.mean(np.diff(onset_idxs)) * (512 / sr))
        else:
            attack_time = 0.0
        return {"mean_attack_time_sec": attack_time}

    def analyze_vibrato(self, data):
        y, sr = data
        pitch = librosa.yin(
            y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
        )
        pitch = pitch[pitch > 0]
        if len(pitch) > 2:
            pitch_diff = np.diff(pitch)
            zero_crossings = np.where(np.diff(np.sign(pitch_diff)))[0]
            duration_sec = len(pitch) / sr
            vibrato_rate = (
                len(zero_crossings) / duration_sec if duration_sec > 0 else 0.0
            )
            vibrato_extent = float(np.std(pitch_diff))
        else:
            vibrato_rate = 0.0
            vibrato_extent = 0.0
        return {"vibrato_rate_hz": vibrato_rate, "vibrato_extent": vibrato_extent}

    def analyze_timbre_consistency(self, data, n_mfcc=13):
        y, sr = data
        n_fft = min(2048, len(y))
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, n_fft=n_fft)
        kl_divs = []
        for i in range(mfccs.shape[1] - 1):
            p = mfccs[:, i] + 1e-6
            q = mfccs[:, i + 1] + 1e-6
            kl = scipy.stats.entropy(p, q)
            if np.isfinite(kl):
                kl_divs.append(kl)
        mean_kl = float(np.mean(kl_divs)) if kl_divs else None
        return {"mean_mfcc_kl_divergence": mean_kl}

    def analyze_polyphony(self, data):
        y, sr = data
        harmonic, _ = librosa.effects.hpss(y)
        S = np.abs(librosa.stft(harmonic))
        poly_features = librosa.feature.poly_features(S=S, sr=sr)

    def analyze_segments(self, ref_segments, sch_segments):
        """Analysiert segmentweise die Referenz- und Schüler-Aufnahmen.

        Diese Funktion führt eine detaillierte Segment-für-Segment-Analyse durch,
        um spezifisches Feedback für verschiedene Abschnitte der Aufnahme zu ermöglichen.

        Args:
            ref_segments: Liste der Referenz-Segmente mit Dateinamen und Zeitstempeln
            sch_segments: Liste der Schüler-Segmente mit Dateinamen und Zeitstempeln

        Returns:
            list: Liste von Analyse-Ergebnissen für jedes Segment-Paar
        """
        segment_results = []

        # Bestimme die maximale Anzahl von Segmenten (längere Aufnahme)
        max_segments = max(len(ref_segments), len(sch_segments))

        # Analysiere jedes Segment-Paar
        for i in range(max_segments):
            # Hole entsprechende Segmente (falls vorhanden)
            ref_seg = ref_segments[i] if i < len(ref_segments) else None
            sch_seg = sch_segments[i] if i < len(sch_segments) else None

            # Analysiere nur wenn beide Segmente existieren
            if ref_seg and sch_seg:
                # Führe vollständige Audio-Analyse für dieses Segment-Paar durch
                analysis = self.analyze_all(ref_seg["filename"], sch_seg["filename"])

                # Sammle Segment-Informationen und Analyse-Ergebnisse
                segment_results.append(
                    {
                        "segment": i + 1,  # Segment-Nummer (1-basiert)
                        "referenz_start": ref_seg["start_sec"],
                        "referenz_end": ref_seg["end_sec"],
                        "schueler_start": sch_seg["start_sec"],
                        "schueler_end": sch_seg["end_sec"],
                        "analysis": analysis,  # Vollständige Feature-Analyse
                    }
                )

        return segment_results

    def build_prompt_generic(self, results, include_explanations=True):
        """Erstellt einen generischen Prompt für die Analyse-Ergebnisse."""
        explanations = {
            # Liste von Erklärungen für die verschiedenen Analyse-Features
            "length": "Länge",
            "loudness": "Lautstärke",
            "pitch": "Tonhöhe",
            "dynamics": "Dynamik",
            "spectral_centroid": "Spektraler Schwerpunkt",
            "onset_count": "Anzahl der Einsätze",
            "rhythm_stability": "Rhythmische Stabilität",
            "spectral_bandwidth": "Spektrale Bandbreite",
            "spectral_rolloff": "Spektraler Roll-Off",
            "silences": "Pausen",
            "zero_crossing_rate": "Nulldurchgangsrate",
            "mel-frequency cepstral coefficients": "Klangfarben-Merkmale",
            "chroma-key": "Tonart",
            "chord_histogram": "Akkord-Verteilung",
            "attack_time": "Anschlag",
            "vibrato": "Vibrato",
            "timbre_consistency": "Klangfarbe-Konstanz",
            "polyphony": "Mehrstimmigkeit",
        }

        detailed_explanations = {
            # Detaillierte Erklärungen nur für den kontextuellen Modus
            "length": "Länge (Gesamtdauer der Aufnahme in Sekunden):",
            "loudness": "Lautstärke (durchschnittliche, maximale und minimale Lautstärke der Aufnahme):",
            "pitch": "Tonhöhe (durchschnittliche, höchste und tiefste Tonhöhe, z.B. wie hoch oder tief gespielt oder gesungen wurde):",
            "dynamics": "Dynamik (Unterschiede zwischen leisen und lauten Stellen, d.h. wie ausdrucksvoll gespielt wurde):",
            "spectral_centroid": "Spektraler Schwerpunkt (zeigt, ob der Klang eher hell oder dunkel ist):",
            "onset_count": "Anzahl der Einsätze (wie oft neue Töne oder Schläge beginnen):",
            "rhythm_stability": "Rhythmische Stabilität (wie gleichmäßig der Rhythmus ist):",
            "spectral_bandwidth": "Spektrale Bandbreite (wie breit das Klangspektrum ist, d.h. wie vielfältig die Frequenzen sind):",
            "spectral_rolloff": "Spektraler Roll-Off (zeigt an, wie viel Energie in den hohen Frequenzen liegt):",
            "silences": "Pausen (Anzahl und Länge der musikalischen Pausen):",
            "zero_crossing_rate": "Nulldurchgangsrate (wie oft das Signal die Nulllinie kreuzt, zeigt Rauschen oder Perkussivität an):",
            "mel-frequency cepstral coefficients": "Klangfarben-Merkmale (beschreiben den Charakter des Klangs, oft für Sprach- und Instrumentenerkennung verwendet):",
            "chroma-key": "Tonart (geschätzte Grundtonart des Stücks):",
            "chord_histogram": "Akkord-Histogramm (häufigste Akkorde im Stück):",
            "attack_time": "Anschlagszeit (wie schnell die Töne nach dem Anschlag lauter werden, zeigt Artikulation wie Staccato oder Legato an):",
            "vibrato": "Vibrato (periodische Schwankungen der Tonhöhe, z.B. Ausdruck beim Singen oder bei Streichinstrumenten):",
            "timbre_consistency": "Klangfarben-Konsistenz (wie konsistent die Klangfarbe über die Zeit ist):",
            "polyphony": "Polyphonie-Grad (wie viele verschiedene Töne gleichzeitig erklingen, z.B. bei Klavier oder Gitarre):",
        }

        lines = []
        for name, _ in self.analysis_functions:
            reference = results.get(f"referenz_{name}")
            student = results.get(f"schueler_{name}")

            if include_explanations:
                explanation = detailed_explanations.get(name, name.capitalize() + ":")
                lines.append(
                    f"{explanation}\n  Referenz = {reference}\n  Schüler = {student}\n"
                )
            else:
                simple_name = explanations.get(name, name.capitalize())
                lines.append(
                    f"{simple_name}:\n Referenz={reference}, Schüler={student} \n"
                )

        ref_chords = results.get("referenz_chord_histogram", {}).get(
            "most_common_chords"
        )
        student_chords = results.get("schueler_chord_histogram", {}).get(
            "most_common_chords"
        )
        if ref_chords and student_chords:
            if include_explanations:
                lines.append(
                    f"Akkordvergleich:\n  Häufigste Akkorde (Referenz): {', '.join(ref_chords)}\n  Häufigste Akkorde (Schüler): {', '.join(student_chords)}\n"
                )
            else:
                lines.append(
                    f"Akkordvergleich: Referenz={', '.join(ref_chords)}, Schüler={', '.join(student_chords)}"
                )

        if include_explanations:
            lines.append(
                "Vergleich der Musikaufnahmen (Zusammenfassung wichtiger Unterschiede):"
            )
        else:
            lines.append("\nVergleichsmetriken:")

        # Vergleichsmetriken (verkürzt für data_only)
        lines.append(
            f"{'- Klangfarben-Ähnlichkeitswert' if include_explanations else 'mfcc_distance'}: {results['mfcc_distance']:.2f}{' (zeigt, wie ähnlich die Klangfarbe ist)' if include_explanations else ''}"
        )

        harmonic_similarity = results.get("chroma_similarity")
        if harmonic_similarity is not None:
            lines.append(
                f"{'- Harmonische Ähnlichkeit' if include_explanations else 'chroma_similarity'}: {harmonic_similarity:.2f}{' (zeigt, wie ähnlich die Harmonie ist)' if include_explanations else ''}"
            )

        dynamic_correlation = results.get("rms_correlation")
        if dynamic_correlation is not None:
            lines.append(
                f"{'- Lautstärkeverlauf-Korrelation' if include_explanations else 'rms_correlation'}: {dynamic_correlation:.2f}{' (zeigt, wie ähnlich die dynamischen Verläufe sind)' if include_explanations else ''}"
            )

        temporal_distance = results.get("dtw_distance")
        if temporal_distance is not None:
            lines.append(
                f"{'- Zeitliche Distanz der Klangfarbe' if include_explanations else 'dtw_distance'}: {temporal_distance:.2f}{' (zeigt, wie unterschiedlich die zeitlichen Verläufe der Klangfarbe sind)' if include_explanations else ''}"
            )

        energy_correlation = results.get("energy_envelope_correlation")
        if energy_correlation is not None:
            lines.append(
                f"{'- Energieverlauf-Korrelation' if include_explanations else 'energy_envelope_correlation'}: {energy_correlation:.2f}{' (zeigt, wie ähnlich die Energieverläufe sind)' if include_explanations else ''}"
            )

        pitch_contour_correlation = results.get("pitch_contour_correlation")
        if pitch_contour_correlation is not None:
            lines.append(
                f"{'- Tonhöhenverlauf-Korrelation' if include_explanations else 'pitch_contour_correlation'}: {pitch_contour_correlation:.2f}{' (zeigt, wie ähnlich die Tonhöhenverläufe sind)' if include_explanations else ''}"
            )

        return "\n".join(lines)

    def _build_system_prompt(
        self,
        language,
        referenz_instrument,
        schueler_instrument,
        personal_message,
        use_simple_language=False,
    ):
        """Erstellt den System-Prompt für kontextuelles Feedback."""
        personal_message_section = self._build_personal_message_section(personal_message)

        simple_language_note = ""
        if use_simple_language:
            simple_language_note = "\n Wichtiger Hinweis: Bitte gib das Feedback besonders einfach, klar und mit möglichst kurzen Sätzen, damit es für einen Schüler mit Sprachbarrieren oder Lernschwierigkeiten leicht verständlich ist.\n"

        return (
            "Hintergrund: Im Folgenden erhältst du Daten zu zwei Musik-Aufnahmen. "
            "Die eine Aufnahme stammt von einer Lehrkraft und dient als Referenz, "
            "die andere Aufnahme ist von einem Schüler, der versucht, die Aufnahme der Lehrkraft nachzuspielen.\n"
            f"Die Referenzaufnahme wurde mit folgendem Instrument aufgenommen: {referenz_instrument}.\n"
            f"Die Schüleraufnahme wurde mit folgendem Instrument aufgenommen: {schueler_instrument}.\n"
            "Aufgabe: Analysiere die Musikaufnahmen und gib dem Schüler ein konstruktives Feedback zu seiner Ausführung im Vergleich zur Referenzaufnahme.\n"
            f"Sprache: Bitte antworte in {language}. Sei freundlich und höflich! "
            "Formuliere die Ergebnisse so, dass sie für einen Schüler der Sekundarstufe 1 (Alter: 12-16) verständlich sind. "
            "Das bedeutet der Fokus liegt auf der Musik und nicht auf den technischen Begriffen oder genauen Messwerten.\n"
            f"{simple_language_note} \n"
            f"{personal_message_section}"
            "Anweisungen:\n"
            "Sollte in den Daten eine Unterteilung in Segmente erfolgen, dann gib sowohl Feedback zu einzelnen Abschnitten, als auch zur Gesamtleistung.\n"
            "Halte es kurz: Maximal 1-3 Sätze sollen zu jedem Segment gegeben werden.\n"
            "Berücksichtige auch die Möglichkeit, dass Segmente zwischen Schüler- und Referenzaufnahme nicht synchron sein könnten. "
            "Zum Beispiel könnte es einen Versatz geben, wenn der Schüler nach einem Fehler die Aufnahme neu startet oder sich während des Stücks verspielt. "
            "Prüfe daher auch versetzte Segmentkombinationen auf bessere Übereinstimmungen und frage im Zweifel nach, ob Fehler aufgetreten sind.\n"
            "Beachte, dass die Aufnahmen unterschiedlich lang sein können. Die kürzere Aufnahme wird am Ende mit Stille aufgefüllt, "
            "damit beide Aufnahmen die gleiche Länge haben. Erwähne dies bitte nicht im Gespräch mit dem Schüler.\n"
            "\n\n"
            "**Begrüßung und Erklärung** Beginne das Gespräch, begrüße den Schüler und erkläre, dass du seine Musik analysiert hast. "
            "Weise den Schüler darauf hin, dass du sein Musik-KI-Assistent bist.\n"
            "\n"
            "Nun folgt das Feedback: Orientiere dich bitte an folgender Struktur:\n"
            "**Lob**: Sage dem Schüler, was er bereits gut gemacht hat. Übertreibe nicht mit dem Lob, sondern bleibe ehrlich und konkret.\n"
            "**Fehleranalyse**: Welche Fehler sind dir aufgefallen? Was hat der Schüler falsch gemacht? Wo weicht er von der Referenz ab?\n"
            "**Tipps und Verbesserungsvorschläge**: Worauf soll der Schüler besonders achten? Wie könnte er die Probleme des Segments verbessern? Welche Übungen könnten helfen?\n"
            "**Zusammenfassung**: Fasse die wichtigsten Punkte zusammen und gib dem Schüler eine klare Handlungsempfehlung für die nächsten Schritte. "
            "Biete auch weitere Hilfe und die Möglichkeit zu Rückfragen an.\n\n"
        )

    def _build_personal_message_section(self, personal_message):
        """Erstellt den Abschnitt für persönliche Nachrichten/Hinweise."""
        if personal_message and personal_message.strip():
            return f"Zusätzliche Hinweise: {personal_message.strip()}\n"
        else:
            return ""

    def generate_feedback_prompt(
        self,
        segment_results,
        language,
        referenz_instrument,
        schueler_instrument,
        personal_message,
        prompt_type="contextual",
        use_simple_language=False,  # <-- NEU: Parameter ergänzt
    ):
        """Generiert den kompletten Feedback-Prompt basierend auf dem gewählten Typ.
        
        Returns:
            dict: Dictionary mit 'system_prompt' (Text zum Kopieren) und 'analysis_data' (Daten für separate Datei)
        """
        # System-Prompt ist immer der gleiche
        system_prompt = self._build_system_prompt(
            language,
            referenz_instrument,
            schueler_instrument,
            personal_message,
            use_simple_language,  # <-- NEU
        )

        # Erstelle Analyse-Daten im gleichen Format wie vorher (als Text)
        analysis_data_text = ""
        
        for seg in segment_results:
            analysis_data_text += f"\nSegment {seg['segment']} ({seg['referenz_start']:.2f}s–{seg['referenz_end']:.2f}s):\n"
            analysis_data_text += self.build_prompt_generic(
                seg["analysis"], prompt_type == "contextual"
            )

        return {
            "system_prompt": system_prompt,
            "analysis_data": analysis_data_text
        }

    def analyze_and_generate_feedback(
        self,
        ref_segments,
        sch_segments,
        language,
        referenz_instrument,
        schueler_instrument,
        personal_message,
        prompt_type="contextual",
        use_simple_language=False,  # <-- NEU: Parameter ergänzt
    ):
        """Hauptfunktion: Führt komplette Analyse durch und generiert Feedback-Prompt."""
        # Führe segmentweise Analyse durch
        segment_results = self.analyze_segments(ref_segments, sch_segments)

        # Generiere strukturierten Feedback-Prompt basierend auf den Analyse-Ergebnissen
        feedback_result = self.generate_feedback_prompt(
            segment_results,
            language,
            referenz_instrument,
            schueler_instrument,
            personal_message,
            prompt_type,
            use_simple_language,  # <-- NEU
        )

        # Rückgabe aller relevanten Informationen
        return {
            "segment_results": segment_results,  # Detaillierte Analyse-Ergebnisse
            "system_prompt": feedback_result["system_prompt"],  # Text-Prompt zum Kopieren
            "analysis_data": feedback_result["analysis_data"],  # Daten für separate Datei
            "language": language,  # Verwendete Sprache
            "segments_analyzed": len(segment_results),  # Anzahl analysierter Segmente
            "prompt_type": prompt_type,  # Verwendeter Prompt-Typ
        }
