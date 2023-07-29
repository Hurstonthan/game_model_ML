import tensorflow as tf
from keras.callbacks import TensorBoard

class CustomTensorBoard(TensorBoard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.writer = tf.summary.create_file_writer(self.log_dir)

    def set_model (self,model):
        pass
    
    #Overrided, saves logs with our step number
    def on_epoch_end(self, epoch, logs=None):
        self.update_stats(**logs)

    def on_batch_end(self, batch, logs=None):
        pass

    def on_train_end(self, _):
        pass
    
    def update_stats(self, **stats):
        self._write_logs(stats,self.step)

    # def on_epoch_end(self, episode, logs=None):
        
    #     if logs is not None:
    #         reward = logs.get('episode_reward')
    #         summary = tf.Summary(value = [tf.Summary.Value(tag = 'Episode Reward', simple_value = reward)])
    #         self.writer.add_summary(summary,episode)
    