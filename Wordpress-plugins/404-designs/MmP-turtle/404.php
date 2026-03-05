<?php
/**
 * The template for displaying 404 pages (not found)
 *
 * @package MomentumPath
 */

// Exit if accessed directly
if (!defined('ABSPATH')) {
    exit;
}
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Page Not Found | <?php bloginfo('name'); ?></title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f1e8;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            color: #2c3e50;
        }

        .container {
            background: white;
            border-radius: 12px;
            padding: 60px 40px;
            max-width: 750px;
            width: 100%;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            text-align: center;
            border-left: 4px solid #c9a961;
        }

        .error-code {
            font-size: 100px;
            font-weight: 900;
            color: #b8a676;
            line-height: 1;
            margin-bottom: 15px;
            letter-spacing: -5px;
        }

        h1 {
            font-size: 28px;
            color: #2c3e50;
            margin-bottom: 15px;
            font-weight: 700;
        }

        .message {
            font-size: 16px;
            color: #546e7a;
            margin-bottom: 30px;
            line-height: 1.7;
        }

        #gameCanvas {
            width: 100%;
            height: 300px;
            background: #e8e4d8;
            border-radius: 8px;
            margin: 20px 0;
            cursor: pointer;
            display: block;
        }

        .game-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            font-size: 14px;
            color: #546e7a;
        }

        .score {
            font-size: 20px;
            font-weight: bold;
            color: #b8a676;
        }

        .instruction {
            font-size: 14px;
            color: #888;
            margin-bottom: 20px;
        }

        .links {
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
        }

        .btn {
            display: inline-block;
            padding: 12px 28px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 15px;
            transition: all 0.3s ease;
            letter-spacing: 0.3px;
        }

        .btn-primary {
            background: #b8a676;
            color: white;
        }

        .btn-primary:hover {
            background: #a89566;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(184, 166, 118, 0.3);
        }

        .btn-secondary {
            background: white;
            color: #b8a676;
            border: 2px solid #b8a676;
        }

        .btn-secondary:hover {
            background: #b8a676;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(184, 166, 118, 0.25);
        }

        @media (max-width: 600px) {
            .container {
                padding: 40px 25px;
            }

            .error-code {
                font-size: 80px;
            }

            h1 {
                font-size: 24px;
            }

            .message {
                font-size: 15px;
            }

            #gameCanvas {
                height: 250px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="error-code">404</div>
        <h1>Page Not Found</h1>
        <p class="message">
            A turtle moves slowly but surely. Sometimes being fast isn't the solution. But if turtle reads MomentumPath articles, it's like strapping a rocket on turtle.
        </p>
        
        <div class="game-info">
            <div class="instruction">Press SPACE or TAP to jump</div>
            <div class="score">Score: <span id="score">0</span></div>
        </div>
        
        <canvas id="gameCanvas"></canvas>
        
        <div class="links">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="btn btn-primary">Go Home</a>
            <a href="<?php echo esc_url(home_url('/blog')); ?>" class="btn btn-secondary">Browse Blog</a>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        
        // Set canvas size
        function resizeCanvas() {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        // Game variables
        let turtle = {
            x: 80,
            y: 200,
            width: 40,
            height: 30,
            dy: 0,
            gravity: 0.6,
            jumpPower: -12,
            grounded: false
        };

        let obstacles = [];
        let trail = [];
        let score = 0;
        let gameSpeed = 4;
        let frame = 0;
        let gameOver = false;
        let gameStarted = false;

        const groundY = canvas.height - 50;

        // Draw turtle with rocket
        function drawTurtle() {
            // Rainbow trail
            for (let i = trail.length - 1; i >= 0; i--) {
                const t = trail[i];
                const alpha = i / trail.length * 0.5;
                const colors = ['#FF6B6B', '#FFA500', '#FFD700', '#90EE90', '#87CEEB', '#DDA0DD'];
                ctx.fillStyle = colors[i % colors.length];
                ctx.globalAlpha = alpha;
                ctx.fillRect(t.x, t.y + 10, 20, 10);
            }
            ctx.globalAlpha = 1;

            // Rocket flame
            ctx.fillStyle = '#FF6B6B';
            ctx.beginPath();
            ctx.moveTo(turtle.x - 10, turtle.y + 15);
            ctx.lineTo(turtle.x - 20 + Math.random() * 5, turtle.y + 10);
            ctx.lineTo(turtle.x - 20 + Math.random() * 5, turtle.y + 20);
            ctx.closePath();
            ctx.fill();

            // Turtle shell (blocky)
            ctx.fillStyle = '#5a7c4f';
            ctx.fillRect(turtle.x, turtle.y, turtle.width, turtle.height);
            
            // Shell pattern
            ctx.fillStyle = '#3d5438';
            ctx.fillRect(turtle.x + 5, turtle.y + 5, 10, 10);
            ctx.fillRect(turtle.x + 20, turtle.y + 5, 10, 10);
            ctx.fillRect(turtle.x + 12, turtle.y + 15, 10, 10);

            // Head
            ctx.fillStyle = '#6b8c5f';
            ctx.fillRect(turtle.x + 35, turtle.y + 10, 15, 12);
            
            // Eye
            ctx.fillStyle = '#000';
            ctx.fillRect(turtle.x + 45, turtle.y + 13, 3, 3);

            // Legs
            ctx.fillStyle = '#6b8c5f';
            ctx.fillRect(turtle.x + 5, turtle.y + 25, 8, 8);
            ctx.fillRect(turtle.x + 25, turtle.y + 25, 8, 8);

            // Rocket (simplified)
            ctx.fillStyle = '#ccc';
            ctx.fillRect(turtle.x - 15, turtle.y + 8, 15, 15);
            ctx.fillStyle = '#999';
            ctx.fillRect(turtle.x - 15, turtle.y + 11, 15, 3);
        }

        // Draw obstacles
        function drawObstacles() {
            ctx.fillStyle = '#8b7355';
            obstacles.forEach(obs => {
                // Rock/log
                ctx.fillRect(obs.x, obs.y, obs.width, obs.height);
                ctx.fillStyle = '#6b5345';
                ctx.fillRect(obs.x + 5, obs.y + 5, obs.width - 10, obs.height - 10);
                ctx.fillStyle = '#8b7355';
            });
        }

        // Draw ground
        function drawGround() {
            ctx.fillStyle = '#c9a961';
            ctx.fillRect(0, groundY, canvas.width, 2);
        }

        // Collision detection
        function checkCollision() {
            for (let obs of obstacles) {
                if (turtle.x < obs.x + obs.width &&
                    turtle.x + turtle.width > obs.x &&
                    turtle.y < obs.y + obs.height &&
                    turtle.y + turtle.height > obs.y) {
                    return true;
                }
            }
            return false;
        }

        // Update game
        function update() {
            if (!gameStarted || gameOver) return;

            frame++;
            
            // Update turtle physics
            turtle.dy += turtle.gravity;
            turtle.y += turtle.dy;

            // Ground collision
            if (turtle.y + turtle.height >= groundY) {
                turtle.y = groundY - turtle.height;
                turtle.dy = 0;
                turtle.grounded = true;
            } else {
                turtle.grounded = false;
            }

            // Add trail
            if (frame % 3 === 0) {
                trail.push({ x: turtle.x - 20, y: turtle.y });
                if (trail.length > 15) trail.shift();
            }

            // Spawn obstacles
            if (frame % 90 === 0) {
                obstacles.push({
                    x: canvas.width,
                    y: groundY - 30,
                    width: 30,
                    height: 30
                });
            }

            // Update obstacles
            obstacles.forEach(obs => {
                obs.x -= gameSpeed;
            });

            // Remove off-screen obstacles and update score
            obstacles = obstacles.filter(obs => {
                if (obs.x + obs.width < 0) {
                    score++;
                    document.getElementById('score').textContent = score;
                    if (score % 10 === 0) gameSpeed += 0.5;
                    return false;
                }
                return true;
            });

            // Check collision
            if (checkCollision()) {
                gameOver = true;
            }
        }

        // Draw everything
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            drawGround();
            drawObstacles();
            drawTurtle();

            if (!gameStarted) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                ctx.font = '24px Arial';
                ctx.fillText('Press SPACE or TAP to start', canvas.width / 2 - 150, canvas.height / 2);
            }

            if (gameOver) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#fff';
                ctx.font = 'bold 32px Arial';
                ctx.fillText('Game Over!', canvas.width / 2 - 80, canvas.height / 2 - 20);
                ctx.font = '20px Arial';
                ctx.fillText('Score: ' + score, canvas.width / 2 - 50, canvas.height / 2 + 20);
                ctx.font = '16px Arial';
                ctx.fillText('Press SPACE or TAP to restart', canvas.width / 2 - 120, canvas.height / 2 + 50);
            }
        }

        // Game loop
        function gameLoop() {
            update();
            draw();
            requestAnimationFrame(gameLoop);
        }

        // Jump function
        function jump() {
            if (!gameStarted) {
                gameStarted = true;
                return;
            }
            
            if (gameOver) {
                // Reset game
                turtle.y = 200;
                turtle.dy = 0;
                obstacles = [];
                trail = [];
                score = 0;
                gameSpeed = 4;
                frame = 0;
                gameOver = false;
                gameStarted = false;
                document.getElementById('score').textContent = '0';
                return;
            }
            
            if (turtle.grounded) {
                turtle.dy = turtle.jumpPower;
            }
        }

        // Controls
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space') {
                e.preventDefault();
                jump();
            }
        });

        canvas.addEventListener('click', jump);
        canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            jump();
        });

        // Start game loop
        gameLoop();
    </script>
</body>
</html>