class QueueManager:
    def __init__(self):
        self.max_queue_size = 10
        self.queue = []
    
    # ----------------------------
    # ADD PLAYER
    # ----------------------------
    def add_player(self, user_id, username):
        
        if any(player['user_id'] == user_id for player in self.queue):
            return f"{username} is already in the queue."
        
        if (len(self.queue) >= self.max_queue_size):
            return "The queue is full. Please wait for the next round."
        
        # Add player to the queue
        self.queue.append({'user_id': user_id, 'username': username})
        
        if len(self.queue) == self.max_queue_size:
            teams = self.create_teams()
            return (f"{username} has been added to the queue. ({len(self.queue)}/{self.max_queue_size})"
                    f"The queue is now full. Teams have been created: {teams}")
        
        return f"{username} has been added to the queue. ({len(self.queue)}/{self.max_queue_size})"
    
    # ----------------------------
    # REMOVE PLAYER
    # ----------------------------
    def remove_player(self, user_id, username):
        for player in self.queue:
            if player['user_id'] == user_id:
                self.queue.remove(player)
                return f"{username} has been removed from the queue. ({len(self.queue)}/{self.max_queue_size})"
            
        return f"{username} is not in the queue."
    
    # ----------------------------
    # VIEW QUEUE
    # ----------------------------
    def view_queue(self):
        if not self.queue:
            return "The queue is currently empty."
        
        queue_list = "\n".join(
            [f"{idx+1}. {player['username']}" for idx, player in enumerate(self.queue)]
        )
        
        return f"Current Queue ({len(self.queue)}/{self.max_queue_size}):\n{queue_list}"

    # ----------------------------
    # CLEAR QUEUE
    # ----------------------------
    def clear_queue(self):
        self.queue.clear()
        return "The queue has been reset."
    
    # ----------------------------
    # GENERATE TEAMS
    # ----------------------------
    def create_teams(self):
        team1 = self.queue[:5]
        team2 = self.queue[5:]
        
        team_a_list = "\n".join([f"{player['username']}" for player in team1])
        team_b_list = "\n".join([f"{player['username']}" for player in team2])
        
        self.clear_queue()  # Clear the queue after creating teams
        
        return (
            f"🔵 Team A:\n{team_a_list}\n\n"
            f"🔴 Team B:\n{team_b_list}"
        )