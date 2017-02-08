#!/usr/bin/python
import numpy as np
import tensorflow as tf
from DCGAN import DCGAN
from Data_Prep import Data_Prep
import cv2
import scipy.misc

def train_fn(nEpochs,image_path):
    '''Function to train DCGAN
        Input: nIter: Number of epochs to train DCGAN'''
    dcgan = DCGAN(batch_size=128,inp_size=4,output_size=64,z_dim=100,caption_dim=2400,learning_rate=1e-3)
    dp = Data_Prep(image_path,batch_size=dcgan.batch_size,nImgs=8000,img_size=dcgan.output_size)
    loss,vars,outs = dcgan.build_model()
    for var in vars['vars_g']:
        print var.name,var.get_shape()
    for var in vars['vars_d']:
        print var.name,var.get_shape()
    d_optim = tf.train.GradientDescentOptimizer(learning_rate=dcgan.learning_rate).minimize(loss['loss_d'],var_list=vars['vars_d'])
    g_optim = tf.train.AdamOptimizer(learning_rate=dcgan.learning_rate).minimize(loss['loss_g'],var_list=vars['vars_g'])
    sess = tf.Session()
    sess.run(tf.initialize_all_variables())
    saver = tf.train.Saver()
    n = int(dp.nImgs*nEpochs/dcgan.batch_size)
    curr_loss_g = curr_loss_d = 1.
    for i in range(n):
        real_imgs,real_captions,wrong_captions = dp.read_batch(overfit=False)
        z = np.random.uniform(-1,1,size=[dcgan.batch_size,dcgan.z_dim])
        if i%5==0 or (curr_loss_g/curr_loss_d)<3.:
            _,curr_loss_d,d_real,d_fake,d_wrong,gen_imgs = sess.run([d_optim,loss['loss_d'],
                                                            outs['disc_real'],
                                                            outs['disc_fake'],
                                                            outs['disc_wrong'],
                                                            outs['gen_imgs']],
                                                            feed_dict={dcgan.z:z,
                                                            dcgan.real_caption:real_captions,
                                                            dcgan.wrong_caption:wrong_captions,
                                                            dcgan.real_images:real_imgs,
                                                            dcgan.train:True})
        _,curr_loss_g = sess.run([g_optim,loss['loss_g']],feed_dict={dcgan.z:z,
                                                                    dcgan.real_caption:real_captions,
                                                                    dcgan.train:True})
        _,curr_loss_g = sess.run([g_optim,loss['loss_g']],feed_dict={dcgan.z:z,
                                                                    dcgan.real_caption:real_captions,
                                                                    dcgan.train:True})
        if i%1 == 0:
            print "Iteration {0} Training loss:\nD_Loss:{1} \tG_Loss:{2}".format(i,curr_loss_d,curr_loss_g)
            gen_imgs = sess.run(dcgan.gen_imgs,feed_dict={dcgan.z:z,
                                                        dcgan.real_caption:real_captions,
                                                        dcgan.train:False})
            print "Mean real_D: {0} \t Mean fake_D: {1} \t Mean wrong_D: {2}".format(np.mean(d_real),
                                                                                    np.mean(d_fake),
                                                                                    np.mean(d_wrong))
            print "Min output:{0} \t Max output:{1}".format(np.min(gen_imgs),np.max(gen_imgs))
            print "Mean generated:{0} \t Mean real:{1}".format(np.mean(gen_imgs),np.mean(real_imgs))
        if i%100==0:
            for j in range(25):
                scipy.misc.imsave('../Output/' + str(j) + '_' + str(i) + '_Gen.jpg',gen_imgs[j])
            np.save('../Output/' + str(i) + '.npy',real_captions[0:25])
    saver.save(sess,'../ckpt/' + str(dcgan.batch_size) + '_' +str(nIter))

if __name__=="__main__":
    train_fn(nEpochs=10,image_path = '../jpg/')
