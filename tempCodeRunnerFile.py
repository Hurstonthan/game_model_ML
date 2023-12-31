for i in range(1,100001):
    state = env.reset()

    epochs,penalties,reward = 0, 0, 0
    done = False

    while not done:
        if random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()
        else: 
            action = np.argmax(q_table[state])

        next_state,reward,done, info = env.step(action)

        old_value = q_table[state,action]
        next_max = np.max(q_table[next_state])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state,action] = new_value

        state= next_state
        epochs += 1

    if i % 100 == 0:
        print(f"Episode: {i}")

print("Trainning finished.\n")


