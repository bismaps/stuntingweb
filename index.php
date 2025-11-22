<?php
$result = null;
$error = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $usia = $_POST['usia'] ?? 0;
    $tinggi = $_POST['tinggi'] ?? 0;
    $berat = $_POST['berat'] ?? 0;
    $gender = $_POST['gender'] ?? 'L';

    $payload = json_encode([
        'usia_bulan' => (int)$usia,
        'tinggi_badan' => (float)$tinggi,
        'berat_badan' => (float)$berat,
        'gender' => $gender
    ]);

    $ch = curl_init('http://127.0.0.1:5000/predict');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json',
        'Content-Length: ' . strlen($payload)
    ]);

    $response = curl_exec($ch);
    
    if ($response === false) {
        $error = "Server AI sedang offline. Pastikan backend Flask berjalan.";
    } else {
        $result = json_decode($response, true);
        if (isset($result['error'])) {
            $error = "Error dari AI: " . $result['error'];
            $result = null;
        }
    }
    curl_close($ch);
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stunting Prediction System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen flex flex-col items-center py-10 px-4">

    <!-- Header -->
    <header class="mb-10 text-center">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-emerald-100 text-emerald-600 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        </div>
        <h1 class="text-3xl font-bold text-slate-800">AI Stunting Detector</h1>
        <p class="text-slate-500 mt-2">Sistem deteksi dini stunting pada anak berbasis AI</p>
    </header>

    <!-- Main Card -->
    <main class="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden border border-slate-100">
        
        <!-- Result Section -->
        <?php if ($error): ?>
            <div class="bg-red-50 border-l-4 border-red-500 p-4 m-6 mb-0 rounded-r">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700"><?php echo htmlspecialchars($error); ?></p>
                    </div>
                </div>
            </div>
        <?php endif; ?>

        <?php if ($result): ?>
            <?php 
                $status = $result['status'];
                // Add 'Stunting' to the list of stunting statuses
                $is_stunting = in_array($status, ['Sangat Pendek', 'Pendek', 'Stunting']);
                $bg_color = $is_stunting ? 'bg-red-50' : 'bg-emerald-50';
                $text_color = $is_stunting ? 'text-red-700' : 'text-emerald-700';
                $border_color = $is_stunting ? 'border-red-200' : 'border-emerald-200';
                $icon_color = $is_stunting ? 'text-red-400' : 'text-emerald-400';
            ?>
            <div class="<?php echo $bg_color; ?> border <?php echo $border_color; ?> rounded-xl p-5 m-6 mb-0">
                <div class="flex items-start">
                    <div class="flex-shrink-0 mt-1">
                        <?php if ($is_stunting): ?>
                            <svg class="h-6 w-6 <?php echo $icon_color; ?>" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                        <?php else: ?>
                            <svg class="h-6 w-6 <?php echo $icon_color; ?>" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                        <?php endif; ?>
                    </div>
                    <div class="ml-4 w-full">
                        <h3 class="text-lg font-bold <?php echo $text_color; ?>">Status: <?php echo htmlspecialchars($status); ?></h3>
                        <div class="mt-2 text-sm <?php echo $text_color; ?> opacity-90">
                            <p>Confidence: <span class="font-semibold"><?php echo htmlspecialchars($result['confidence']); ?></span></p>
                            <p class="mt-1 text-xs"><?php echo htmlspecialchars($result['message']); ?></p>
                        </div>
                    </div>
                </div>
            </div>
        <?php endif; ?>

        <!-- Form -->
        <div class="p-6">
            <form method="POST" action="" class="space-y-5">
                
                <div class="grid grid-cols-2 gap-4">
                    <!-- Usia -->
                    <div>
                        <label for="usia" class="block text-sm font-medium text-slate-700 mb-1">Usia (Bulan)</label>
                        <div class="relative rounded-md shadow-sm">
                            <input type="number" name="usia" id="usia" required min="0" max="60" 
                                   class="focus:ring-emerald-500 focus:border-emerald-500 block w-full pl-3 pr-12 sm:text-sm border-slate-300 rounded-md py-2 border" 
                                   placeholder="0" value="<?php echo isset($_POST['usia']) ? htmlspecialchars($_POST['usia']) : ''; ?>">
                            <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                                <span class="text-slate-500 sm:text-sm">Bln</span>
                            </div>
                        </div>
                    </div>

                    <!-- Gender -->
                    <div>
                        <label for="gender" class="block text-sm font-medium text-slate-700 mb-1">Jenis Kelamin</label>
                        <select id="gender" name="gender" class="focus:ring-emerald-500 focus:border-emerald-500 block w-full sm:text-sm border-slate-300 rounded-md py-2 border bg-white">
                            <option value="L" <?php echo (isset($_POST['gender']) && $_POST['gender'] === 'L') ? 'selected' : ''; ?>>Laki-laki</option>
                            <option value="P" <?php echo (isset($_POST['gender']) && $_POST['gender'] === 'P') ? 'selected' : ''; ?>>Perempuan</option>
                        </select>
                    </div>
                </div>

                <!-- Tinggi -->
                <div>
                    <label for="tinggi" class="block text-sm font-medium text-slate-700 mb-1">Tinggi Badan (cm)</label>
                    <div class="relative rounded-md shadow-sm">
                        <input type="number" name="tinggi" id="tinggi" required step="0.1" min="0" 
                               class="focus:ring-emerald-500 focus:border-emerald-500 block w-full pl-3 pr-12 sm:text-sm border-slate-300 rounded-md py-2 border" 
                               placeholder="0.0" value="<?php echo isset($_POST['tinggi']) ? htmlspecialchars($_POST['tinggi']) : ''; ?>">
                        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                            <span class="text-slate-500 sm:text-sm">cm</span>
                        </div>
                    </div>
                </div>

                <!-- Berat -->
                <div>
                    <label for="berat" class="block text-sm font-medium text-slate-700 mb-1">Berat Badan (kg)</label>
                    <div class="relative rounded-md shadow-sm">
                        <input type="number" name="berat" id="berat" required step="0.1" min="0" 
                               class="focus:ring-emerald-500 focus:border-emerald-500 block w-full pl-3 pr-12 sm:text-sm border-slate-300 rounded-md py-2 border" 
                               placeholder="0.0" value="<?php echo isset($_POST['berat']) ? htmlspecialchars($_POST['berat']) : ''; ?>">
                        <div class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                            <span class="text-slate-500 sm:text-sm">kg</span>
                        </div>
                    </div>
                </div>

                <!-- Submit Button -->
                <div class="pt-2">
                    <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 transition-colors duration-200">
                        Analisa Sekarang
                    </button>
                </div>

            </form>
        </div>
        <div class="bg-slate-50 px-6 py-4 border-t border-slate-100">
            <p class="text-xs text-center text-slate-400">
                &copy; 2025 Stunting Prediction System. Hybrid Microservices.
            </p>
        </div>
    </main>

</body>
</html>
