#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import numpy as np

class TextureFactory(object):
    """
    A factory to generate a checkerboard background where the luminance value of each block 
    is uniformly drawn from the given luminance_values with variable transparency circles.
    
    Example Usage:

 >>> f_c = TextureFactory('checkerboard',10,image_width=200)
>>> img_c = f_c.get_image(.5, .25, bg_luminance=.5)
>>> f_r = TextureFactory('random',2,image_width=200)
>>> img_r = f_r.get_image(1, .5)

    Parameters
    ----------
    block_width : int
        Determines the "granularity" of the texture.
    luminance_values : tuple[float], optional
    image_width : int, optional
    """

    def __init__(self, mode, block_width, luminance_values=(0., 1.), image_width=480):
        self.image_width = image_width

        if mode == 'random':
            n_blocks = int(np.ceil(image_width / block_width))
            r = np.ndarray((n_blocks, n_blocks))
            for i in range(block_width):
                for j in range(block_width):
                    if (i % 5) == 0: r[i][j] = luminance_values[j % 5]
                    if (i % 5) == 1: r[i][j] = luminance_values[(j + 1) % 5]
                    if (i % 5) == 2: r[i][j] = luminance_values[(j + 2) % 5]
                    if (i % 5) == 3: r[i][j] = luminance_values[(j + 3) % 5]
                    if (i % 5) == 4: r[i][j] = luminance_values[(j + 4) % 5]

            t = np.repeat(np.repeat(r, block_width, axis=0), block_width, axis=1)
            self.texture = t[:image_width, :image_width]

        elif mode == 'checkerboard':
            self.texture = np.ndarray((image_width, image_width))
            for i, j in np.ndindex((image_width, image_width)):
                x = (i // block_width) % 2
                y = (j // block_width) % 2
                self.texture[i, j] = luminance_values[0] if x == y else luminance_values[4]
        else:
            raise ValueError("invalid mode")



    def get_image(self, tau, alpha, circle_radius=150, bg_luminance=None, stack_option='none'):
        """
        Adds the transparency circle and optionally a cutout background, and returns the image.
        Underlying texture remains unchanged for reuse.

        Parameters
        ----------
        tau, alpha: float
            alpha blending params of transparency circle.
        circle_radius : int, optional
        
        Returns
        -------
        np.ndarray
            Grayscale image as a square matrix with values between 0 and 1.
        """
        image = self.texture.copy()

        # compute distances from image center (=radius) of each pixel
        x = np.linspace(-0.5 * self.image_width, 0.5 * self.image_width, self.image_width)
        radii = np.sqrt((x ** 2)[np.newaxis] + (x ** 2)[:, np.newaxis])

        # add transparent circle
        idx = radii <= circle_radius
        image[idx] = alpha * image[idx] + (1 - alpha) * tau
        
        before_cutout = image.copy()

        # cut out center and fill in background
        if bg_luminance is not None:
            idx = radii > circle_radius
            image[idx] = bg_luminance

        if stack_option == 'none':
            return image
        elif stack_option == 'horizontal':
            return np.block([before_cutout, image])
        elif stack_option == 'vertical':
            return np.block([[before_cutout], [image]])
        elif stack_option == 'both':
            return np.block([[before_cutout, image], [image, before_cutout]])
        else:
            raise ValueError('Invalid value given for stack_option.')
            
            
